# --------- Imports ----------
from balethon import Client
from balethon.objects import Message
from balethon.conditions import at_state 
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
# --------- client ----------
bot = Client("YourClient")
# ---------------------------------

# --------- Configuration ----------
DPI = 300                    # OCR image quality
OCR_LANG = "fas+eng"         # Persian + English
TEXT_THRESHOLD = 50          # Text length threshold to detect scanned PDFs
# ---------------------------------

# --------- Functions For Extracting PDF ----------
def extract_text_from_pdf(pdf_path):
    """Extract text from text-based PDFs"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
            text += "\n#######################\n"
    except Exception as e:
        text = "قابل خواندن نبود"
        return text
    
    return text

def ocr_pdf(pdf_path):
    """Run OCR on scanned PDFs"""
    text = ""
    try:
        images = convert_from_path(pdf_path, dpi=DPI)
        for i, img in enumerate(images):
            page_text = pytesseract.image_to_string(
                img,
                lang=OCR_LANG,
                config="--psm 6"
            )
            text += f"\n\n--- Page {i + 1} ---\n"
            text += page_text
    except Exception as e:
        text = "قابل خواندن نبود"
        return text
        
    return text

def extract_any_pdf(pdf_path):
    """Smart extractor: text-based first, OCR if needed"""
    try:
        text = extract_text_from_pdf(pdf_path)
        if len(text.strip()) >= TEXT_THRESHOLD:
            return text
        else:
            return ocr_pdf(pdf_path)
    except:
        return("قابل خواندن نبود!!!")

def save_output(path:str):
    final_text = extract_any_pdf(path)
    # Save output
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(final_text)
# ---------------------------------

# --------- A Function For Send Choped Messages ----------
def chopped_text(path:str , n:int) :
    """A Function For Send Choped Messages"""
    txt = []
    nline = 0
    txt3 = ""
    chopped_txt = []
    # read out put file and clean text
    with open(path , 'rb') as output:
        lines = output.read().decode()
        line = [lines.split("\r\n")]
        txt = line[0]
    
    # chopped lines
    for element in txt:
        txt3 += str(element)+"  #  "
        nline += 1
        if nline % n == 0:
            chopped_txt.append(txt3)
            txt3 = ""
    # defender 
    if txt[0] == "قابل خواندن نبود":
        return txt[0]
                
    return chopped_txt 
# ---------------------------------

        
# --------- Main Bot ----------

# --------- Start Bot ----------
@bot.on_message(at_state(None))
async def start(message:Message):
    if message.text == "/start":
        await message.reply("سلام 👋 خوش اومدی! فایل PDF رو بفرست ببینیم چی داره 😉")
        message.author.set_state("File")


# ---------  Get File And Send Output ----------
@bot.on_message(at_state("File"))
async def text(message:Message):
    downloading = await message.reply("دارم دانلودش می‌کنم… یکم صبر کن ⏳") 
    response = await bot.download(message.document.id) # downlod file
    # ---------Downlod File---------
    try:
        with open("downloaded file.pdf", "wb") as file:
            file.write(response)
        await downloading.edit_text("گرفتمش 👍 الان دارم نگاهش می‌کنم")
    except:
        await message.reply("اِ… این که PDF نیست 😅 لطفاً یه فایل PDF درست بفرست")
    
    # --------- Save Output ---------
    save_output("downloaded file.pdf")
    
    # --------- Send Chopped Message Or Send Text File ---------
    txt_out= chopped_text("output.txt" , 150)
    if txt_out == "قابل خواندن نبود" or txt_out == [] :
        await downloading.edit_text("نتونستم این فایل رو بخونم 😕 اگه می‌تونی یه فایل دیگه بفرست") 
    elif len(txt_out) <10:
        for one_txt in txt_out:
            await message.reply(one_txt)
    elif len(txt_out)>=10:
        await message.reply_document("output.txt")
    # --------- Delete State ---------
    message.author.del_state()
    

# --------- Run Bot ---------

bot.run()

# --------- The End ---------