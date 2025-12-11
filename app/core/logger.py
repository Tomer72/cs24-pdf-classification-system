import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout), # מדפיס למסך (בשביל דוקר/פיתוח)
            logging.FileHandler("debug.log", encoding='utf-8') # <--- התוספת: שומר לקובץ
        ]
    )
    # משתיק רעשים
    logging.getLogger("multipart").setLevel(logging.WARNING)