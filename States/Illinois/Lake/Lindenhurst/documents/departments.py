from json.decoder import JSONDecodeError
from os import terminal_size, write
import requests
from bs4 import BeautifulSoup
from json import load, dump
import re


class Departments:
    def __init__(self) -> None:
        self.departments = None
        self.completed = set()
        try:
            if self.loadJSON() is False:
                self.storeJSON(writeBaseData=True)
                self.loadJSON()
        except FileNotFoundError:
            self.storeJSON(writeBaseData=True)
            self.loadJSON()

    def loadJSON(self) -> bool:
        with open("departments.json", "r") as file:
            try:
                self.departments = load(file)
            except JSONDecodeError:
                return False
            file.close()
        return True

    def storeJSON(self, writeBaseData: bool = False) -> int:
        if writeBaseData:
            self.departments = {
                "Home Page": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=1&page=4_1"
                ],
                "Messages From the Mayor": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=2&page=4_1"
                ],
                "Village Board": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=3&page=4_1"
                ],
                "Village Commissions": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=4&page=4_1"
                ],
                "Administration": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=5&page=4_1"
                ],
                "Building and Engineering": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=6&page=4_1"
                ],
                "Police": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=7&page=4_1"
                ],
                "Public Works": [
                    "https://www.lindenhurstil.org/egov/apps/document/center.egov?view=browse&eGov_searchTitle=&eGov_searchType=&&eGov_searchCategory=&eGov_searchTopic=&eGov_searchYear=&app=4&sect=content&path=&act=&id=&order=&eGov_searchDepartment=8&page=4_1"
                ],
            }
        with open("departments.json", "w") as file:
            dump(self.departments, file)
            file.close()

    def getAllPages(self) -> None:
        for department in self.departments.keys():
            lastPage = -1
            url = self.departments[department][-1]
            tempResponse = requests.get(url).text
            soup = BeautifulSoup(markup=tempResponse, features="lxml")
            pages = soup.findAll(name="a", attrs={"class": "eGov_pageLink"})

            currentPage = re.findall("(page\=)([^&]+)", url)[0][1]

            currentPage = int(currentPage[currentPage.index("_") + 1 :])

            try:
                lastPage = int(pages[-1].text)
            except IndexError:
                lastPage = 1

            if currentPage != lastPage:
                templateURL = url[: url.index(re.findall("(page\=)([^&]+)", url)[0][1])]
                for pageNumber in range(lastPage + 1):
                    if pageNumber <= currentPage:
                        pass
                    else:
                        self.departments[department].append(
                            templateURL + "4_" + str(pageNumber)
                        )
                self.storeJSON()

            if currentPage >= lastPage:
                self.completed.add(department)

        if len(self.completed) != 8:
            self.getAllPages()

    def getAllReports(self) -> dict:
        responses = {}
        for department in self.departments.keys():

            dateList = []
            titleList = []
            typeList = []
            urlList = []

            for url in self.departments[department]:
                response = requests.get(url).text
                soup = BeautifulSoup(markup=response, features="lxml")

                titles = soup.findAll(name="td", attrs={"class": "eGov_DataCell3"})
                # urls = soup.findAll(name="a", attrs={"class": "eGov_listItemLink"})
                dates = soup.findAll(name="td", attrs={"class": "eGov_listSortDesc"})
                types = soup.findAll(name="td", attrs={"class": "eGov_DataCell2"})

                for title in titles:
                    titleList.append(title.text.strip().replace("\n", ""))
                    for url in title.children:
                        urlList.append(url.get("href"))

                for date in dates:
                    dateList.append(date.text.strip().replace("\n", ""))

                for type in types:
                    for image in type.children:  # There is only object in this iterator
                        typeList.append(image.get("alt").strip().replace("\n", ""))

            if len(dateList) == len(titleList) == len(typeList) == len(urlList):
                for item in range(len(dateList)):
                    hashCode = dateList[item].replace("/", "") + titleList[item][0:3]
                    responses[hashCode] = [
                        dateList[item],
                        titleList[item],
                        typeList[item],
                        urlList[item],
                    ]

        return responses
