from lxml import etree
import os
import re
import json

# XPath implementation
def extract_with_xpath():

    
    print("\n--------------------------------RTVSLO 1--------------------------------\n")
    rtvslo("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html")
    print("\n--------------------------------RTVSLO 2--------------------------------\n")
    rtvslo("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html")
    

    print("\n-------------------------------OVERSTOCK 1------------------------------\n")
    overstock("../input-extraction/overstock.com/jewelry01.html")
    print("\n-------------------------------OVERSTOCK 2------------------------------\n")
    overstock("../input-extraction/overstock.com/jewelry02.html")

    print("\n--------------------------------AVTONET 1-------------------------------\n")
    avtonet("../input-extraction/avto.net/audi.html")
    print("\n--------------------------------AVTONET 2-------------------------------\n")
    avtonet("../input-extraction/avto.net/BMW M3 , letnik_2017,61800 EUR - prodam __ Avtonet __ www.Avto.net.html")


def rtvslo(filePath):
    #absolutePath = os.path.abspath(filePath)
    currentDir = os.path.dirname(__file__)
    fullPath = os.path.join(currentDir, filePath)
    with open(fullPath, 'r', encoding='utf-8') as file:
        htmlContent = file.read()

    tree = etree.HTML(htmlContent)

    author = tree.xpath("//div[@class='author-name']/text()")[0] # !
    publishMeta = tree.xpath("//div[@class='publish-meta']/text()")
    publishedTime = publishMeta[0]
    publishedTime = re.sub(r"^\s*", "", publishedTime) # ! (to remove leading \n \t, r = raw string, to handle "\" characters properly)
    title = tree.xpath("//header[@class='article-header']/h1/text()")[0] # !
    subTitle = tree.xpath("//header[@class='article-header']/div[@class='subtitle']/text()")[0] # !
    lead = tree.xpath("//p[@class='lead']/text()")[0] # !
    content = tree.xpath("//article[@class='article']/p/text() | //article[@class='article']/p/strong/text()")

    contentList = [] # !
    for line in content:
        contentList.append(line)

    data = {}
    data["Author"] = author
    data["PublishedTime"] = publishedTime
    data["Title"] = title
    data["Subtitle"] = subTitle
    data["Lead"] = lead
    data["Content"] = contentList
    jsonData = json.dumps(data, indent=4, ensure_ascii=False)
    print(jsonData)


def overstock(filePath):
    currentDir = os.path.dirname(__file__)
    fullPath = os.path.join(currentDir, filePath)
    with open(fullPath, 'r') as file:
        htmlContent = file.read()

    tree = etree.HTML(htmlContent)

    rows = tree.xpath("/html/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr")

    data = []

    for row in rows:
        contentTd = row.xpath("td[2]")
        if contentTd:
            title = row.xpath("td[2]/a/b/text()")[0] # !
            info = row.xpath("td[2]/table/tbody/tr")[0]
            listPrice = info.xpath("td[1]/table/tbody/tr[1]/td[2]/s/text()")[0] # !
            price = info.xpath("td[1]/table/tbody/tr[2]/td[2]/span/b/text()")[0] # !
            disc = info.xpath("td[1]/table/tbody/tr[3]/td[2]/span/text()")[0]
            disc = re.split(r'\s+', disc)
            saving = disc[0] # !
            savingPercent = disc[1] # ! 
            content = info.xpath("td[2]/span/text()")[0] # !
            content = re.sub(r'\n', ' ', content)
            data.append({"Title": title, "ListPrice": listPrice, "Price": price, "Saving": saving, "SavingPercent": savingPercent, "Content": content})

    jsonData = json.dumps(data, indent=4)
    print(jsonData)


def avtonet(filePath):
    currentDir = os.path.dirname(__file__)
    fullPath = os.path.join(currentDir, filePath)
    with open(fullPath, 'r') as file:
        htmlContent = file.read()

    tree = etree.HTML(htmlContent)

    titleInfo = tree.xpath("/html/body/strong/div[1]/div/div/div[1]/div/div")[0]
    titleSep = titleInfo.xpath("h3/text() | h3//strong/text()")
    titleSep[0] = re.sub(r'\xa0', ' ', titleSep[0])
    title = '' # !
    if(len(titleSep) == 1):
        title = titleSep[0]
    else:
        title = titleSep[0] + titleSep[1]

    detailsInfo = tree.xpath("/html/body/strong/div[1]/div/div/div[2]/div/div[1]/div[3]/div")[0]

    firstRegistration = detailsInfo.xpath("div[1]//h5/text()")[0] # !
    firstRegistration = re.sub(r'\n', '', firstRegistration)
    firstRegistration = firstRegistration.strip()
    firstRegistration = re.sub(r'\xa0', ' ', firstRegistration)

    distanceDrivenSep = detailsInfo.xpath("div[2]//h5/text() | div[2]//h5/small/text()")
    distanceDrivenSep[0] = re.sub(r'\n', '', distanceDrivenSep[0])
    distanceDrivenSep[0] = distanceDrivenSep[0].strip()
    distanceDrivenSep[0] = re.sub(r'\xa0', ' ', distanceDrivenSep[0])
    distanceDriven = distanceDrivenSep[0] + ' ' + distanceDrivenSep[1] # !

    numberOfOwners = detailsInfo.xpath("div[3]//h5/text()")[0] # !
    numberOfOwners = re.sub(r'\n', '', numberOfOwners)
    numberOfOwners = numberOfOwners.strip()

    fuelType = detailsInfo.xpath("div[4]//h5/text()")[0] # !

    enginePowerSep = detailsInfo.xpath("div[5]//h5/text() | div[5]//h5/small/text()")
    enginePowerSep[0] = re.sub(r'\n', '', enginePowerSep[0])
    enginePowerSep[0] = enginePowerSep[0].strip()
    enginePowerSep[0] = re.sub(r'\xa0', ' ', enginePowerSep[0])
    enginePowerSep[2] = re.sub(r'\n', '', enginePowerSep[2])
    enginePowerSep[2] = enginePowerSep[2].strip()
    enginePowerSep[2] = re.sub(r'\xa0', ' ', enginePowerSep[2])
    enginePower = enginePowerSep[0] + ' ' + enginePowerSep[1] + ' ' + enginePowerSep[2] + ' ' + enginePowerSep[3] # !

    gearbox = detailsInfo.xpath("div[6]//h5/text()")[0] # !

    rows = tree.xpath("/html/body/strong/div[1]/div/div/div[2]/div/div[1]/div[4]/table[1]/tbody/tr[position() > 1]") # position() > 1 => skip first row, because it doesn't have data
    contentDict = {} # !
    for row in rows:
        rowName = row.xpath("th/text()")[0]
        rowData = row.xpath("td/text()")[0]
        rowData = re.sub(r'\n', '', rowData)
        rowData = re.sub(r'\t', '', rowData)
        rowData = rowData.strip()
        rowData = re.sub(r'\xa0', ' ', rowData)
        contentDict[rowName] = rowData

    price = tree.xpath("/html/body/strong/div[1]/div/div/div[3]/div[2]/div[1]/div/div/p[1]/text()")[0] # !
    price = re.sub(r'\n', '', price)
    price = price.strip()

    data = {}
    data["Title"] = title
    data["FirstRegistration"] = firstRegistration
    data["DistanceDriven"] = distanceDriven
    data["NumberOfOwners"] = numberOfOwners
    data["FuelType"] = fuelType
    data["EnginePower"] = enginePower
    data["Gearbox"] = gearbox
    data["Content"] = contentDict
    data["Price"] = price

    jsonData = json.dumps(data, indent=4, ensure_ascii=False)
    print(jsonData)