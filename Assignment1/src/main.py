from crawler import Crawler

c = Crawler([
    'https://www.gov.si/', 
    'https://evem.gov.si/', 
    'https://e-uprava.gov.si/', 
    'https://www.e-prostor.gov.si/'
    ], 
    worker_count=10
)

c.run()