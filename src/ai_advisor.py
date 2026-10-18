import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# قائمة سوداء للبروتوكولات الربوية (التي تعتمد على الفوائد التقليدية)
HARAM_PROTOCOLS = ["aave", "compound", "morpho", "euler", "venus", "silo"]


def is_halal(protocol_name):
    """يتحقق مما إذا كان البروتوكول ليس في القائمة السوداء"""
    if not protocol_name:
        return False
    return protocol_name.lower() not in HARAM_PROTOCOLS


def ask_gemini_about_halal_yields(halal_vaults):
    """يرسل القائمة النظيفة إلى Gemini ليشرحها"""
    if not halal_vaults:
        return "لم يتم العثور على بروتوكولات حلال في هذه اللحظة."

    # تجهيز النص الذي سنرسله لـ Gemini
    vaults_text = "\n".join(
        [
            f"- {v['protocol']} on {v['network']} with {v['apy']} APY"
            for v in halal_vaults
        ]
    )

    prompt = f"""
    أنت مستشار مالي إسلامي خبير في التمويل اللامركزي (DeFi).
    إليك قائمة بالبروتوكولات التي اجتازت الفلترة الأولية (ليست ربوية):
    
    {vaults_text}
    
    اكتب رداً مختصراً جداً باللغة العربية، تشرح فيه للمستخدم:
    1. لماذا هذه البروتوكولات تعتبر "حلال" (مثلاً: تعتمد على رسوم التداول أو المشاركة في السيولة وليس الفوائد).
    2. حذر المستخدم من المخاطر (مثل مخاطر العقود الذكية).
    """

    response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
    return response.text
