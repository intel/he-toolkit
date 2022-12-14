"""Jobs"""
import base64
from os import environ
from threading import Thread

from app.hekit.hekit import decode, decrypt, encode, encrypt
from app.kafka.kafka_producer import KafkaProducer
from app.models.db import db
from app.models.job import Job, generate_job_id
from app.utils.job_utils import (
    check_user_directory,
    create_job_directory,
    load_heql,
    load_payload,
    save_user_request,
)
from flask import Blueprint, Response, jsonify, request, send_file
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session

jobs = Blueprint(name="jobs", import_name=__name__)


def process_encode_encrypt_produce(user_id: str, job_id: str):
    """Process encode, encrypt and produce"""
    # Encode query
    encode_time = encode(user_id, job_id)

    # Encrypt query
    encrypt_time = encrypt(user_id, job_id)

    # Create headers
    heql = load_heql()
    org_id = "0"
    headers = {
        "HEQL": heql,
        "UID": user_id,
        "BID": org_id,
        "JobID": job_id,
    }

    payload = load_payload(user_id, job_id)

    # Produce message to Kafka
    producer = KafkaProducer()
    producer.produce(headers, payload)

    on_done_encode_encrypt_produce(job_id, encode_time, encrypt_time)


def on_done_encode_encrypt_produce(job_id: str, encode_time: str, encrypt_time: str):
    """On done encode, encrypt and produce"""

    engine = create_engine(
        f"postgresql+psycopg2://{environ['SQLALCHEMY_DATABASE_URI_NO_PROTOCOL']}",
        echo=False,
        future=True,
    )
    session = Session(engine, expire_on_commit=False)

    stmt = (
        update(Job)
        .where(Job.job_id == job_id)
        .values(encode=encode_time, encrypt=encrypt_time)
    )

    session.execute(stmt)
    session.commit()

    session.close()


@jobs.route("", methods=["GET"])
@jwt_required()
def get_jobs():
    """Get jobs by user"""
    claims = get_jwt()
    user_jobs = (
        db.session.query(Job)
        .filter(Job.user_id == claims["user_id"])
        .order_by(Job.job_id.desc())
    )
    return jsonify([i.serialize() for i in user_jobs.all()])


@jobs.route("", methods=["POST"])
@jwt_required()
def create_job():
    """
    ---
    post:
      description: Create a job
      responses:
        '200':
          description: Job created
      tags:
          - Jobs
    """
    input_data = request.get_json()

    encoded_base64 = input_data["fileAsBase64"]

    data = encoded_base64[encoded_base64.index(",") + 1 : len(encoded_base64)]
    base64_bytes = data.encode("ascii")
    message_bytes = base64.b64decode(base64_bytes)

    user_id = str(get_jwt_identity())

    job_id = generate_job_id()

    check_user_directory(user_id)

    create_job_directory(user_id, job_id)

    save_user_request(user_id, job_id, message_bytes)

    process = Thread(target=process_encode_encrypt_produce, args=[user_id, job_id])
    process.start()

    # Create job
    org_id = "0"
    job = Job(org_id=org_id, job_id=job_id, status="PENDING", user_id=user_id)
    db.session.add(job)
    db.session.commit()

    return jsonify(job.serialize())


@jobs.route("/<job_id>/status", methods=["GET"])
@jwt_required()
def get_job_status(job_id):
    """Get job status"""
    user_id = get_jwt_identity()
    job = (
        db.session.query(Job)
        .filter(Job.job_id == job_id and Job.user_id == user_id)
        .first()
    )

    return jsonify(job.serialize())


def process_decrypt_decode(user_id: str, job_id: str):
    """Process decrypt and decode"""
    # Decrypt query
    decrypt_time = decrypt(user_id, job_id)

    # Decode query
    decode_time = decode(user_id, job_id)

    on_done_decrypt_decode(job_id, decrypt_time, decode_time)


def on_done_decrypt_decode(job_id: str, decrypt_time: str, decode_time: str):
    """On done decrypt and decode"""
    engine = create_engine(
        f"postgresql+psycopg2://{environ['SQLALCHEMY_DATABASE_URI_NO_PROTOCOL']}",
        echo=False,
        future=True,
    )
    session = Session(engine, expire_on_commit=False)

    status = "DECRYPTED"

    stmt = (
        update(Job)
        .where(Job.job_id == job_id)
        .values(status=status, decrypt=decrypt_time, decode=decode_time)
    )

    session.execute(stmt)
    session.commit()

    session.close()


@jobs.route("/<job_id>/decrypt", methods=["GET"])
@jwt_required()
def decrypt_job_result(job_id):
    """Decrypt job result"""
    user_id = get_jwt_identity()
    job = (
        db.session.query(Job)
        .filter(Job.job_id == job_id and Job.user_id == user_id)
        .one()
    )

    if job.status == "PENDING":
        output = {"result": "Job status PENDING"}
        return jsonify(output)

    process = Thread(target=process_decrypt_decode, args=[user_id, job_id])
    process.start()

    return Response(status=201)


@jobs.route("/<job_id>/result", methods=["GET"])
@jwt_required()
def get_job_result(job_id):
    """Get job result"""
    user_id = get_jwt_identity()
    job = (
        db.session.query(Job)
        .filter(Job.job_id == job_id and Job.user_id == user_id)
        .one()
    )

    if job.status != "DECRYPTED":
        output = {"result": "Job status not decrypted"}
        return jsonify(output)

    result = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_final"

    return send_file(result, as_attachment=True)
