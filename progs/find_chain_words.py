words = [
    "вино",
    "сука",
    "срок",
    "арка",
    "тура",
    "сова",
    "жара",
    "день",
    "жгут",
    "урна",
    "заяц",
    "зона",
    "звук",
    "гора",
    "гусь",
    "руна",
    "суша",
    "тара",
    "враг",
    "арба",
    "кара",
    "поза",
    "бобр",
    "икра",
    "слон",
    "доза",
    "знак",
    "груз",
    "глаз",
    "жаба",
    "база",
    "дока",
    "губа",
    "блин",
    "жена",
    "доля",
    "роса",
    "бита",
    "каюк",
    "друг",
    "вера",
    "заря",
    "дыра",
    "буря",
    "дача",
    "вода",
    "кафр",
    "дума",
    "драп",
    "баян",
    "суха",
    "диво",
    "грач",
    "дочь",
    "брат",
    "дуга",
    "каюр",
    "крюк",
    "звон",
    "пола",
    "вата",
    "град",
    "банк",
    "рука",
    "сока",
    "урюк",
    "иней",
    "дека",
    "борт",
    "бокс",
    "сухо",
    "мура",
    "балл",
    "врач",
    "долг",
    "урок",
    "стон",
    "мука",
    "азот",
    "лука",
    "кафе",
    "жест",
    "вход",
    "волк",
    "муха",
    "блок",
    "гриф",
    "жбан",
    "двор",
    "дело",
    "зима",
    "ваза",
    "рана",
    "сток",
    "змея",
    "каре",
    "горе",
    "полк",
    "роза",
    "арфа",
    "игра",
]


def find_chain_words(
    words: list[str], start_word: str, end_word: str, chain: list[str] | None = None
) -> list[str]:
    if chain is None:
        chain = [start_word]
        s_i = words.index(start_word)
        words = words[s_i + 1 :] + words[:s_i]

    res = recursion_search(words, start_word, end_word, chain)
    return res if end_word in res else []


def recursion_search(
    words: list[str], start_word: str, end_word: str, chain: list[str]
) -> list[str]:
    for i, word in enumerate(words):
        if is_correct_word(word, chain[-1]):
            chain.append(word)
            if word == end_word or len(words) == 1:
                return chain
            first = recursion_search(
                words[i + 1 :] + words[:i], start_word, end_word, chain[:-1]
            )
            second = recursion_search(
                words[i + 1 :] + words[:i], start_word, end_word, chain
            )

            len_f = len(first)
            len_s = len(second)
            f_has_end = first[-1] == end_word
            s_has_end = second[-1] == end_word

            if f_has_end and s_has_end:
                if len_f < len_s:
                    return first
                return second
            elif f_has_end:
                return first
            elif s_has_end:
                return second
    return chain


def is_correct_word(w1: str, w2: str) -> bool:
    return sum(1 for c1, c2 in zip(w1, w2, strict=True) if c1 != c2) == 1


# здесь продолжайте программу
start_word = "тара"
end_word = "сухо"

print(find_chain_words(words, start_word, end_word))
