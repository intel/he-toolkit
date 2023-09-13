# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


class HelloWorlds:
    """This class holds 'hello world' in different languages using the standard 2-letter codes for languages,
    https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    """

    _hello_worlds: dict[str, str] = {
        "AF": "hello wêreld",  # Afrikaans
        "SQ": "përshendetje botë",  # Albanian
        "AR": "مرحبا بالعالم",  # Arabic
        "HY": "բարեւ աշխարհ",  # Armenian
        "AZ": "salam dunya",  # Azerbaijani
        "EU": "kaixo mundua",  # Basque
        "BE": "прывітанне сусвет",  # Belarusian
        "BG": "здравей свят",  # Bulgarian
        "CA": "hola món",  # Catalan
        "ZH": "你好世界",  # Chinese
        "CO": "salutu mondu",  # Corsican
        "HR": "pozdrav svijete",  # Croatian
        "CS": "ahoj světe",  # Czech
        "DA": "hej verden",  # Danish
        "NL": "hallo wereld",  # Dutch
        "EN": "hello world",  # English
        "FI": "hei maailma",  # Finnish
        "FR": "bonjour le monde",  # French
        "KA": "გამარჯობა მსოფლიო",  # Georgian
        "DE": "hallo welt",  # German
        "EL": "γειά σου κόσμε",  # Greek
        "IW": "שלום עולם",  # Hebrew
        "HU": "helló világ",  # Hungarian
        "IS": "halló heimur",  # Icelandic
        "GA": "dia duit ar domhan",  # Irish
        "IT": "ciao mondo",  # Italian
        "JA": "こんにちは世界",  # Japanese
        "KK": "сәлем әлем",  # Kazakh
        "KO": "안녕하세요 세계",  # Korean
        "LA": "salve mundi",  # Latin
        "LV": "sveika pasaule",  # Latvian
        "LT": "labas pasauli",  # Lithuanian
        "MS": "hai dunia",  # Malay
        "MN": "сайн уу ертөнц",  # Mongolian
        "NO": "hei verden",  # Norwegian
        "FA": "سلام دنیا",  # Persian
        "PL": "witaj świecie",  # Polish
        "PT": "olá mundo",  # Portuguese
        "RO": "salut lume",  # Romanian
        "RU": "привет мир",  # Russian
        "SM": "talofa le lalolagi",  # Samoan
        "GD": "hàlo a shaoghail",  # Scottish Gaelic
        "SR": "здраво свете",  # Serbian
        "SK": "ahoj svet",  # Slovak
        "ES": "hola mundo",  # Spanish
        "SU": "halo dunya",  # Sudanese
        "SV": "hej världen",  # Swedish
        "TG": "салом ҷаҳон",  # Tajik
        "TH": "สวัสดีชาวโลก",  # Thai
        "TR": "selam dünya",  # Turkish
        "TK": "salam dünýä",  # Turkmen
        "UK": "привіт світ",  # Ukrainian
        "UR": "ہیلو دنیا",  # Urdu
        "VI": "Chào thế giới",  # Vietnamese
        "CY": "helo byd",  # Welsh
    }

    @classmethod
    def print_msg(cls, args) -> None:
        """Executes new functionality"""
        # Choices in `--lang` should block unknown
        msg = cls._hello_worlds[args.lang]
        print(msg)

    @classmethod
    def get_available_languages(cls) -> list[str]:
        """Returns as a list the available languages"""
        return sorted(cls._hello_worlds.keys())
