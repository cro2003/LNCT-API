import re
import os
import json
import time
import flask
import decimal
import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify

app = Flask(__name__)
class Pages:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {'Host': 'portal.lnct.ac.in', 'Cache-Control': 'no-cache', 'DNT': '1', 'X-Requested-With': 'XMLHttpRequest', 'X-MicrosoftAjax': 'Delta=true', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': '*/*', 'Origin': 'http://portal.lnct.ac.in', 'Referer': 'http://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx', 'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,hi;q=0.7'}
        start = requests.get('http://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx')
        content = start.text
        soup = BeautifulSoup(content, 'html.parser')
        viewstate = soup.find_all(id='__VIEWSTATE')[0]['value']
        viewstategenerator = soup.find_all(id='__VIEWSTATEGENERATOR')[0]['value']
        eventvalidation = soup.find_all(id='__EVENTVALIDATION')[0]['value']
        self.data = {'ctl00$ScriptManager1': 'ctl00$cph1$UpdatePanel5|ctl00$cph1$btnStuLogin', '__VIEWSTATE':viewstate, '__VIEWSTATEGENERATOR':viewstategenerator, '__EVENTVALIDATION': eventvalidation, 'ctl00$cph1$rdbtnlType': '2', 'ctl00$cph1$txtStuUser':username, 'ctl00$cph1$txtStuPsw':password, '__ASYNCPOST':True, 'ctl00$cph1$btnStuLogin':'Login>>'}
        login_page = requests.post('http://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx', headers=self.headers, data=self.data)
        try:
            self.cookies = {"error": BeautifulSoup(login_page.text, 'html.parser').find(id='ctl00_cph1_lblErrMsgStu').get_text()}
        except:
            self.cookies = {'error': None, 'npfwg': '1', 'npf_r': '', 'npf_l': 'lnct.ac.in', 'npf_u': 'https://lnct.ac.in/#', 'ASP.NET_SessionId': login_page.cookies['ASP.NET_SessionId']}

    def profile(self):
        if self.cookies['error'] != None:
            return self.cookies
        else:
            profile_status = requests.get('https://portal.lnct.ac.in/Accsoft2/parents/StudentPersonalDetails.aspx', headers=self.headers, cookies=self.cookies)
            content = profile_status.text
            soup = BeautifulSoup(content, 'html.parser')
            return soup

    def attendancePage(self):
        if self.cookies['error'] != None:
            return self.cookies
        else:
            attendance_status = requests.get('http://portal.lnct.ac.in/Accsoft2/Parents/StuAttendanceStatus.aspx', headers=self.headers, cookies=self.cookies)
            content = attendance_status.text
            soup = BeautifulSoup(content, 'html.parser')
            return soup

    def SubjectAttendancePage(self):
        if self.cookies['error'] != None:
            return self.cookies
        else:
            attendance_status = requests.get('https://portal.lnct.ac.in/Accsoft2/parents/subwiseattn.aspx', headers=self.headers, cookies=self.cookies)
            content = attendance_status.text
            soup = BeautifulSoup(content, 'html.parser')
            return soup

    def FeesPage(self, params=None):
        if self.cookies['error'] != None:
            return self.cookies
        else:
            if params==None:
                fees_Status = requests.get('https://portal.lnct.ac.in/Accsoft2/Parents/FeesReceipts.aspx', headers=self.headers, cookies=self.cookies)
            else:
                fees_Status = requests.post('https://portal.lnct.ac.in/Accsoft2/Parents/FeesReceipts.aspx', cookies=self.cookies, data=params)
            content = fees_Status.text
            soup = BeautifulSoup(content, 'html.parser')
            return soup

@app.route("/")
def home():
    return "<head><h1> Docs </h1></head><br> <body> 1) /api/profile[username]&[password] => Profile Information <br> 2) /api/attendancePercentage[username]&[password] => Attendance Percentage <br> 3) /api/attendanceDatewise[username]&[password] => Attendance Status sorted on the basis of Datewise <br> 4) /api/attendanceSubjectwise[username]&[password] => Subjectwise Attendance  <br> 5) /api/feeStatus[username]&[password] => Information About the Fees Paid <br> <p><b>NOTE: Kindly Put Username & Password in the place of [username] & [password] respectively! <b><p></body>"

@app.route("/api/profile<username>&<password>")
def profile(username, password):
    main = Pages(username, password)
    soup = main.profile()
    try:
        name = soup.find(id="ctl00_ContentPlaceHolder1_txtStudName")['value']
        enrollId = soup.find(id="ctl00_ContentPlaceHolder1_txtUEnrollNo")['value']
        ScholarId = soup.find(id="ctl00_ContentPlaceHolder1_txtBoardRollNo")['value']
        AccsoftId = soup.find(id="ctl00_ContentPlaceHolder1_txtEnrollNo")['value']
        course = soup.find(id="messagesDropdown").get_text().strip()
        t = (re.sub(' +', ' ', course))
        g = "".join([s for s in t.strip().splitlines(True) if s.strip()])
        courseInfo = g.replace('\r','').replace('\n','').split(" ")
        course = courseInfo[1]
        branch = courseInfo[2]
        semester = courseInfo[4]
        section = courseInfo[5]
        MNumber = soup.find(id="ctl00_ContentPlaceHolder1_txtSMob")['value']
        email = soup.find(id="ctl00_ContentPlaceHolder1_txtSEmail")['value']
        StuImage = soup.find(id="ctl00_ContentPlaceHolder1_imgphoto")['src']
        product = {"name": name, "course": course, "branch": branch, "semester": semester, "section": section, "enrollmentId": enrollId, "scholarId": ScholarId, "accsoftId": AccsoftId, "MobileNumber": MNumber, "email": email, "profileImage": StuImage}
        return jsonify(product)
    except:
        return jsonify(soup)

@app.route("/api/attendancePercentage<username>&<password>")
def attendancePercentage(username, password):
    main = Pages(username, password)
    soup = main.attendancePage()
    try:
        name = re.sub(' +', ' ', soup.find_all(class_='mr-2 d-none d-lg-inline text-gray-600 small')[0].get_text().replace('\n', '').replace('\r', ''))[1:]
        TotalLectures = int(re.sub('\D', '', soup.find_all(id='ctl00_ContentPlaceHolder1_lbltotperiod')[0].get_text()))
        present = int(re.sub('\D', '', soup.find_all(id='ctl00_ContentPlaceHolder1_lbltotalp')[0].get_text()))
        absent = int(re.sub('\D', '', soup.find_all(id='ctl00_ContentPlaceHolder1_lbltotala')[0].get_text()))
        percentage = decimal.Decimal(present*100/TotalLectures)
        percentage = round(percentage,2)
        product = {"name":name, "totalLectures":TotalLectures, "present":present, "absent":absent, "percentage": f"{percentage}"}
        return jsonify(product)
    except:
        return jsonify(soup)

@app.route("/api/attendanceDatewise<username>&<password>")
def attendanceDatewise(username, password):
    main = Pages(username, password)
    soup = main.attendancePage()
    try:
        name = re.sub(' +', ' ', soup.find_all(class_='mr-2 d-none d-lg-inline text-gray-600 small')[0].get_text().replace('\n', '').replace('\r', ''))[1:]
        table = soup.find('table', class_='mGrid')
        table = table.find_all('tr')
        day = table[1].find_all("td")[1].get_text()
        subject = table[1].find_all("td")[3].get_text()
        status = table[1].find_all("td")[4].get_text()
        product = {"name": name, "attendance":[{"day": day, "main": [{"subject": subject, "status": status}]}]}
        product = json.dumps(product)
        product = json.loads(product)
        previous_day = table[1].find_all('td')[1].get_text()
        for main in table:
            try:
                date = main.find_all('td')[1].get_text()
                subject = main.find_all('td')[3].get_text()
                status = main.find_all('td')[4].get_text()
                if previous_day == date:
                    for x in product['attendance']:
                        if x['day'] == date:
                            if x['main'][0]['subject'] != subject:
                                x['main'].append([{ "subject": subject, "status": status }])
                elif previous_day != date:
                    product['attendance'].append({ 'day': date, 'main': [{ 'subject': subject, 'status': status }] })
                previous_day = date
            except IndexError:pass
        return jsonify(product)
    except:
        return jsonify(soup)

@app.route("/api/attendanceSubjectwise<username>&<password>")
def attendanceSubjectwise(username, password):
    main = Pages(username, password)
    soup = main.SubjectAttendancePage()
    try:
        name = re.sub(' +', ' ', soup.find_all(class_='mr-2 d-none d-lg-inline text-gray-600 small')[0].get_text().replace('\n', '').replace('\r', ''))[1:]
        product = {"name":name, "attendance":[]}
        table = soup.find(class_="mGrid")
        table = table.find_all("tr")
        for main in table:
            try:
                row = main.find_all('td')
                subject = row[0].get_text()
                ssn = row[1].get_text()
                TotalLectures = int(row[2].get_text())
                AttendedLectures = int(row[3].get_text())
                product["attendance"].append({"subject":subject, "subShort":ssn, "totalLectures": TotalLectures, "present": AttendedLectures, "absent": TotalLectures - AttendedLectures})
            except IndexError:pass
        return jsonify(product)
    except:
        return jsonify(soup)

@app.route("/api/feeStatus<username>&<password>")
def feesStatus(username, password):
    main = Pages(username, password)
    soup = main.FeesPage()
    try:
        product = {"name": re.sub(' +', ' ', soup.find_all(class_='mr-2 d-none d-lg-inline text-gray-600 small')[0].get_text().replace('\n', '').replace('\r', ''))[1:], "feesInfo":[]}
        feelo = []
        for x in soup.find_all('option'):
            val = x['value']
            data = {'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ddlfinyear', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'], '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'], '__VIEWSTATEENCRYPTED': '', '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'], 'ctl00$ContentPlaceHolder1$hdnNoOfPrntCopy': '1', 'ctl00$ContentPlaceHolder1$hdnrid': '', 'ctl00$ContentPlaceHolder1$ddlfinyear': val}
            soup = main.FeesPage(data)
            table = soup.find(id='ctl00_ContentPlaceHolder1_VSFlexGrid1')
            for z in table.find_all('tr'):
                if z.find_all('th')==[]:
                    date = z.find_all('td')[2].get_text().replace('\n','')
                    voucherNumber = z.find_all('td')[3].get_text().replace('\n','')
                    ttlAmt = z.find_all('td')[4].get_text().replace('\n','')
                    value = {"txnDate": date, "VNumber": voucherNumber, "totalAmt": ttlAmt}
                    feelo.append(value)
        product['feesInfo'].append(list(reversed(feelo)))
        return jsonify(product)
    except:
        return jsonify(soup)
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])
