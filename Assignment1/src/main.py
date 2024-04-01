from crawler import Crawler

c = Crawler([
    'https://www.gov.si/', 
    'https://spot.gov.si/', 
    'https://e-uprava.gov.si/', 
    'https://www.e-prostor.gov.si/'
    ], 
    worker_count=1
)

c.run()