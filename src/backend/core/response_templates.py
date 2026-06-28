import random
from typing import Literal

from src.backend.core.config import BOT_NAME, DOMAIN_NAME


CONTACT_TEMPLATE_VALUES = {
    "phone_main": "034-219364-66 ต่อ 25520",
    "mobile": "089-979-7911",
    "fax": "034-241971",
    "facebook": "Department of Electrical Engineering - Silpakorn University",
    "website": "https://ee-eng.su.ac.th/",
    "address": (
        "ภาควิชาวิศวกรรมไฟฟ้า คณะวิศวกรรมศาสตร์และเทคโนโลยีอุตสาหกรรม "
        "มหาวิทยาลัยศิลปากร วิทยาเขตพระราชวังสนามจันทร์ จ.นครปฐม 73000"
    ),
}

THAI_DOMAIN_NAME = "ภาควิชาวิศวกรรมไฟฟ้า มหาวิทยาลัยศิลปากร"

GREETING_TEMPLATES = (
    "สวัสดีครับ ผมคือ {bot_name} ผู้ช่วยข้อมูลของ{domain_name} ถามเรื่องหลักสูตร รายวิชา อาจารย์ หรือช่องทางติดต่อได้เลยครับ",
    "สวัสดีครับ ผมคือ {bot_name} ช่วยดูข้อมูลเกี่ยวกับ{domain_name}ได้ ทั้งหลักสูตร รายวิชา อาจารย์ เอกสาร และข้อมูลติดต่อครับ",
    "สวัสดีครับ {bot_name} พร้อมช่วยครับ ถ้าต้องการข้อมูลของ{domain_name} เช่น หลักสูตร อาจารย์ รายวิชา หรือการติดต่อ ส่งคำถามมาได้เลยครับ",
    "สวัสดีครับ ผมคือ {bot_name} ยินดีให้ข้อมูลของ{domain_name} ถามได้ทั้งเรื่องหลักสูตร รายวิชา อาจารย์ เอกสาร และข้อมูลติดต่อครับ",
    "สวัสดีครับ ผมคือ {bot_name} ถามข้อมูลเกี่ยวกับ{domain_name}ได้เลยครับ ไม่ว่าจะเป็นหลักสูตร รายวิชา อาจารย์ หรือช่องทางติดต่อครับ",
    "สวัสดีครับ {bot_name} ยินดีช่วยค้นข้อมูลของ{domain_name}ครับ เรื่องหลักสูตร รายวิชา อาจารย์ เอกสาร หรือการติดต่อ ถามมาได้เลยครับ",
)

GREETING_TEMPLATES_EN = (
    "Hello. I'm {bot_name}, the information assistant for {domain_name}. You can ask about the curriculum, courses, lecturers, or contact details.",
    "Hello, nice to meet you. I'm {bot_name}, the information assistant for {domain_name}. Feel free to ask about courses, lecturers, documents, or department contact information.",
    "Hello. {bot_name} can help with official information about {domain_name}, including curriculum, courses, lecturers, documents, and contact details.",
    "Hello. I'm {bot_name}, here to help with {domain_name}. Ask me about curriculum, courses, lecturers, documents, or department contact information.",
    "Hello, I'm happy to help. I'm {bot_name}, the information assistant for {domain_name}. Send any department question my way.",
    "Hello. {bot_name} is ready to help with {domain_name} information, such as curriculum, courses, lecturers, and contact details.",
)

CONTACT_GENERAL_TEMPLATES = (
    """ข้อมูลติดต่อภาควิชามีดังนี้ครับ

- โทรศัพท์: {phone_main}
- มือถือ: {mobile}
- โทรศัพท์/โทรสาร: {fax}
- Facebook: {facebook}""",
    """ติดต่อภาควิชาวิศวกรรมไฟฟ้าได้ตามช่องทางนี้ครับ

- เบอร์หลัก: {phone_main}
- เบอร์มือถือ: {mobile}
- โทรศัพท์/โทรสาร: {fax}
- Facebook: {facebook}""",
)

CONTACT_GENERAL_TEMPLATES_EN = (
    """Department contact details:

- Phone: {phone_main}
- Mobile: {mobile}
- Phone/Fax: {fax}
- Facebook: {facebook}""",
    """You can contact the department through:

- Main phone: {phone_main}
- Mobile: {mobile}
- Phone/Fax: {fax}
- Facebook: {facebook}""",
)

CONTACT_FOCUSED_TEMPLATES = {
    "phone": (
        """เบอร์ติดต่อภาควิชาครับ

- โทรศัพท์: {phone_main}
- มือถือ: {mobile}
- โทรศัพท์/โทรสาร: {fax}""",
        """ช่องทางโทรศัพท์ของภาควิชาคือ

- เบอร์หลัก: {phone_main}
- เบอร์มือถือ: {mobile}
- โทรศัพท์/โทรสาร: {fax}""",
    ),
    "facebook": (
        "Facebook ของภาควิชาคือ {facebook} ครับ",
        "ติดต่อผ่าน Facebook ได้ที่ {facebook} ครับ",
    ),
    "website": (
        "เว็บไซต์ภาควิชาคือ {website} ครับ",
        "เข้าเว็บไซต์ภาควิชาได้ที่ {website} ครับ",
    ),
    "address": (
        "ที่ตั้งภาควิชาคือ {address} ครับ",
        "ภาควิชาตั้งอยู่ที่ {address} ครับ",
    ),
    "email": (
        "ในข้อมูลติดต่อทางการที่ผมมีตอนนี้ยังไม่พบอีเมลภาควิชาโดยตรงครับ แนะนำติดต่อผ่านโทรศัพท์ {phone_main} หรือ Facebook: {facebook}",
        "ตอนนี้ผมยังไม่มีอีเมลภาควิชาในแหล่งข้อมูลทางการที่ใช้อยู่ครับ ใช้เบอร์ {phone_main} หรือ Facebook: {facebook} ได้ครับ",
    ),
}

CONTACT_FOCUSED_TEMPLATES_EN = {
    "phone": (
        """Department phone contacts:

- Phone: {phone_main}
- Mobile: {mobile}
- Phone/Fax: {fax}""",
        """You can call the department through:

- Main phone: {phone_main}
- Mobile: {mobile}
- Phone/Fax: {fax}""",
    ),
    "facebook": (
        "The department Facebook page is {facebook}.",
        "You can contact the department on Facebook: {facebook}.",
    ),
    "website": (
        "The department website is {website}.",
        "You can visit the department website at {website}.",
    ),
    "address": (
        "The department address is {address}.",
        "The department is located at {address}.",
    ),
    "email": (
        "I do not have an official department email in the available contact data. Please use {phone_main} or Facebook: {facebook}.",
        "The official contact data I have does not list a direct department email. You can use {phone_main} or Facebook: {facebook}.",
    ),
}

OUT_OF_SCOPE_SOFT_OPENINGS = (
    "ขอโทษด้วยครับ",
    "ขออภัยนะครับ",
    "น้องไฟฟ้ายังช่วยเรื่องนี้ไม่ได้ครับ",
)

OUT_OF_SCOPE_SOFT_OPENINGS_EN = (
    "Sorry about that.",
    "Sorry.",
    "I can't really help with that one.",
)

OUT_OF_SCOPE_SOFT_CLOSES = {
    "food": (
        "แต่ก็อย่าลืมหาอะไรกินด้วยนะครับ",
        "ถ้าหิวอยู่ ลองหาอะไรรองท้องก่อนนะครับ",
        "แต่อย่าปล่อยให้ท้องว่างนานนะครับ",
    ),
    "rest": (
        "พักสักนิดก็น่าจะช่วยได้นะครับ",
        "ถ้าไหวลองพักสายตาหรือพักผ่อนสักหน่อยนะครับ",
        "อย่าลืมดูแลตัวเองและพักบ้างนะครับ",
    ),
    "stress": (
        "ค่อยๆ พักหายใจลึกๆ สักนิดก็ดีนะครับ",
        "ถ้ารู้สึกหนักเกินไป ลองพักก่อนสักหน่อยนะครับ",
        "ดูแลตัวเองด้วยนะครับ ถ้าพักได้ลองพักก่อนครับ",
    ),
    "generic": (
        "ถ้ามีคำถามเกี่ยวกับภาควิชาเมื่อไร ทักมาได้เลยครับ",
        "ถ้าต้องการข้อมูลเกี่ยวกับภาควิชา ผมพร้อมช่วยต่อครับ",
        "ถ้าอยากคุยเรื่องหลักสูตร อาจารย์ หรือข้อมูลภาควิชา ผมช่วยได้ครับ",
    ),
}

OUT_OF_SCOPE_SOFT_CLOSES_EN = {
    "food": (
        "Don’t forget to grab something to eat too.",
        "If you're hungry, try getting a quick bite first.",
        "Try not to stay hungry for too long.",
    ),
    "rest": (
        "A short break might help.",
        "If you can, try resting your eyes or taking a short break.",
        "Don’t forget to take care of yourself and rest a bit.",
    ),
    "stress": (
        "Try taking a slow breath and a short pause.",
        "If it feels like too much, taking a short break may help.",
        "Please take care of yourself and rest if you can.",
    ),
    "generic": (
        "If you have a question about the department, feel free to ask.",
        "If you need department information, I can help with that.",
        "If you want to ask about courses, lecturers, or department information, I can help.",
    ),
}

OUT_OF_SCOPE_HARD_OPENINGS = (
    "ขออภัยครับ",
    "ขอโทษครับ",
    "น้องไฟฟ้ายังไม่สามารถช่วยเรื่องนี้ได้ครับ",
)

OUT_OF_SCOPE_HARD_OPENINGS_EN = (
    "Sorry.",
    "I’m sorry.",
    "I can’t help with that topic.",
)

OUT_OF_SCOPE_HARD_BODIES = (
    "คำถามนี้อยู่นอกขอบเขตที่ผมรองรับ",
    "คำถามนี้อยู่นอกขอบเขตของระบบ ตอนนี้ผมยังตอบเรื่องนี้ไม่ได้",
    "เรื่องนี้ไม่ใช่ขอบเขตที่ผมถูกออกแบบมาให้ช่วยตอบครับ",
)

OUT_OF_SCOPE_HARD_BODIES_EN = (
    "That question is outside the scope I support.",
    "I can't answer that right now.",
    "That topic is outside what I was designed to help with.",
)

OUT_OF_SCOPE_HARD_CLOSES = (
    "ถ้าต้องการข้อมูลเกี่ยวกับหลักสูตร อาจารย์ เอกสาร หรือข้อมูลติดต่อของ{domain_name} ผมช่วยได้ครับ",
    "หากอยากสอบถามเรื่องของ{domain_name} เช่น รายวิชา หลักสูตร หรือการติดต่อ ผมช่วยต่อได้ครับ",
    "ถ้าคุณมีคำถามเกี่ยวกับ{domain_name}หรือข้อมูลภาควิชา ส่งมาได้เลยครับ",
)

OUT_OF_SCOPE_HARD_CLOSES_EN = (
    "If you need help with the curriculum, lecturers, documents, or contact information for {domain_name}, I can help.",
    "If you want to ask about {domain_name}, such as courses, curriculum, or contact details, I can help with that.",
    "If your question is about {domain_name} or department information, feel free to ask.",
)


def get_bot_name_for_language(language: Literal["th", "en"]) -> str:
    if language == "en":
        return "Nong Faifa (ECS AI Assistant)"
    return BOT_NAME


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split()).strip(" \t\n\r?!.,")


def detect_contact_focus(original_query: str) -> Literal["phone", "facebook", "website", "address", "email", "general"]:
    normalized = _normalize(original_query)
    if any(term in normalized for term in ("facebook", "เฟสบุค", "เฟซบุ๊ก", "fb")):
        return "facebook"
    if any(term in normalized for term in ("website", "เว็บ", "เว็บไซต์", "url")):
        return "website"
    if any(term in normalized for term in ("ที่อยู่", "อยู่ที่ไหน", "office", "address", "location")):
        return "address"
    if any(term in normalized for term in ("email", "e-mail", "อีเมล", "เมล")):
        return "email"
    if any(term in normalized for term in ("เบอร์", "โทร", "phone", "call", "tel")):
        return "phone"
    return "general"


def build_contact_response(language: Literal["th", "en"], original_query: str = "") -> str:
    focus = detect_contact_focus(original_query)
    values = CONTACT_TEMPLATE_VALUES
    if language == "en":
        templates = CONTACT_FOCUSED_TEMPLATES_EN.get(focus) or CONTACT_GENERAL_TEMPLATES_EN
        return random.choice(templates).format(domain_name=DOMAIN_NAME, **values)

    templates = CONTACT_FOCUSED_TEMPLATES.get(focus) or CONTACT_GENERAL_TEMPLATES
    return random.choice(templates).format(domain_name=DOMAIN_NAME, **values)


def build_greeting_response(language: Literal["th", "en"]) -> str:
    templates = GREETING_TEMPLATES if language == "th" else GREETING_TEMPLATES_EN
    domain_name = THAI_DOMAIN_NAME if language == "th" else DOMAIN_NAME
    return random.choice(templates).format(
        bot_name=get_bot_name_for_language(language),
        domain_name=domain_name,
    )


def build_capability_response(language: Literal["th", "en"]) -> str:
    if language == "en":
        return (
            "I can help with official information about the Department of Electrical Engineering, "
            "Silpakorn University, including curriculum, lecturers, staff, courses, documents, "
            "and department contact details."
        )
    return (
        "ผมช่วยตอบคำถามเกี่ยวกับข้อมูลของภาควิชาวิศวกรรมไฟฟ้า มหาวิทยาลัยศิลปากรได้ครับ "
        "เช่น หลักสูตร รายวิชา อาจารย์ บุคลากร เอกสาร และข้อมูลติดต่อของภาควิชา"
    )


def build_soft_out_of_scope_response(theme: str, language: Literal["th", "en"]) -> str:
    if language == "en":
        close = random.choice(OUT_OF_SCOPE_SOFT_CLOSES_EN.get(theme, OUT_OF_SCOPE_SOFT_CLOSES_EN["generic"]))
        return f"{random.choice(OUT_OF_SCOPE_SOFT_OPENINGS_EN)} {close}"
    close = random.choice(OUT_OF_SCOPE_SOFT_CLOSES.get(theme, OUT_OF_SCOPE_SOFT_CLOSES["generic"]))
    return f"{random.choice(OUT_OF_SCOPE_SOFT_OPENINGS)} {close}"


def build_hard_out_of_scope_response(language: Literal["th", "en"]) -> str:
    if language == "en":
        return " ".join(
            [
                random.choice(OUT_OF_SCOPE_HARD_OPENINGS_EN),
                random.choice(OUT_OF_SCOPE_HARD_BODIES_EN),
                random.choice(OUT_OF_SCOPE_HARD_CLOSES_EN).format(domain_name=DOMAIN_NAME),
            ]
        )
    return " ".join(
        [
            random.choice(OUT_OF_SCOPE_HARD_OPENINGS),
            random.choice(OUT_OF_SCOPE_HARD_BODIES),
            random.choice(OUT_OF_SCOPE_HARD_CLOSES).format(domain_name=DOMAIN_NAME),
        ]
    )


def build_out_of_scope_response(
    *,
    variant: str,
    language: Literal["th", "en"],
    theme: str = "generic",
    reason: Literal["weather", "coding"] | None = None,
) -> str:
    if language == "th" and reason == "weather":
        return (
            "คำถามนี้อยู่นอกขอบเขตที่ผมรองรับครับ เพราะเป็นคำถามเกี่ยวกับสภาพอากาศ "
            f"ถ้าต้องการข้อมูลเกี่ยวกับหลักสูตร อาจารย์ เอกสาร หรือข้อมูลติดต่อของ{DOMAIN_NAME} ผมช่วยได้ครับ"
        )
    if language == "th" and reason == "coding":
        return (
            "คำถามนี้อยู่นอกขอบเขตที่ผมรองรับครับ เพราะเป็นคำขอเขียนโค้ดทั่วไป "
            f"ถ้าต้องการข้อมูลเกี่ยวกับหลักสูตร อาจารย์ เอกสาร หรือข้อมูลติดต่อของ{DOMAIN_NAME} ผมช่วยได้ครับ"
        )
    if variant == "soft_oob":
        return build_soft_out_of_scope_response(theme, language)
    return build_hard_out_of_scope_response(language)
