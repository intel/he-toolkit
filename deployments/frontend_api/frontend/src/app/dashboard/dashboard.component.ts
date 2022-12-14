import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { IJob } from '../models/Job';
import { AuthService } from '../services/auth.service';
import { JobService } from '../services/job.service';
import { FormBuilder } from '@angular/forms';
import { interval, map, Observable, Subscription, timer } from 'rxjs';
import { Router } from '@angular/router';

export class FileToUpload {
    // #region Properties (5)

    public fileAsBase64: string = "";
    public fileName: string = "";
    public fileSize: number = 0;
    public fileType: string = "";
    public lastModifiedTime: number = 0;

    // #endregion Properties (5)
}

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, AfterViewInit, OnDestroy {
    // #region Properties (7)

    private theFile: any = null;

    @ViewChild('inputFile')
    inputFile!: ElementRef;
    public jobForm = this.formBuilder.group({
        file: ''
    });
    public jobs: IJob[] = [];
    public jobsSubscription!: Subscription;
    public jobsSubscriptionTimer: Observable<number> = timer(0, 10000);
    public username = "";

    // #endregion Properties (7)

    // #region Constructors (1)

    constructor(private jobService: JobService,
        private authService: AuthService,
        private formBuilder: FormBuilder,
        public router: Router
    ) {
        this.username = this.authService.getDecodedAccessToken().username;
    }

    // #endregion Constructors (1)

    // #region Public Methods (8)

    public decryptJob(jobId: string): void {
        this.jobService.decryptJob(jobId).subscribe();
    }

    public downloadJobResult(jobId: string): void {
        this.jobService.downloadJobResult(jobId).subscribe(
            {
                next: (result: any) => {
                    const blob = new Blob([result], { type: 'application/text' });
                    var downloadURL = window.URL.createObjectURL(result);
                    var link = document.createElement('a');
                    link.href = downloadURL;
                    link.download = `${jobId}_result.txt`;
                    link.click();
                }
            }
        );
    }

    public getJobs(): void {
        this.jobService.getJobs().subscribe(
            {
                next: (result: IJob[]) => {
                    this.jobs = result;
                },
                error: (e) => {
                    console.error(e);
                    if (!this.authService.isLoggedIn()) {
                        this.router.navigate(['login']);
                    }
                },
            }
        );
    }

    public ngAfterViewInit(): void {
        this.jobsSubscription = this.jobsSubscriptionTimer.subscribe(() => {
            this.getJobs();
        });
    }

    public ngOnDestroy() {
        this.jobsSubscription.unsubscribe();
    }

    public ngOnInit(): void {
    }

    public onFileChange(event: any) {
        this.theFile = null;
        if (event.target.files && event.target.files.length > 0) {
            this.theFile = event.target.files[0];
        }
    }

    public uploadFile(): void {
        this.readAndUploadFile(this.theFile);
        this.inputFile.nativeElement.value = "";
    }

    // #endregion Public Methods (8)

    // #region Private Methods (1)

    private readAndUploadFile(theFile: any) {
        let file = new FileToUpload();

        // Set File Information
        file.fileName = theFile.name;
        file.fileSize = theFile.size;
        file.fileType = theFile.type;
        file.lastModifiedTime = theFile.lastModified;

        // Use FileReader() object to get file to upload
        // NOTE: FileReader only works with newer browsers
        let reader = new FileReader();

        // Setup onload event for reader
        reader.onload = () => {
            // Store base64 encoded representation of file
            if (reader.result) {
                file.fileAsBase64 = reader.result.toString();
                this.jobService.createJob(file).subscribe(
                    {
                        next: () => {
                            this.getJobs();
                            this.jobForm.reset();
                        }
                    }
                );
            }
        }

        // Read the file
        reader.readAsDataURL(theFile);
    }

    // #endregion Private Methods (1)
}
