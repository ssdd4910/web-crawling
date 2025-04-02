import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import time
import matplotlib.pyplot as plt
import plotly.express as px



def Jobkorea_searching():
    
    url = "https://www.jobkorea.co.kr/Search/?stext=데이터분석"  # 원하는 검색어에 맞게 설정
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 결과 저장
    results = []

    # 채용 리스트 선택
    articles = soup.select('article.list-item')

    for item in articles:
        company = item.select_one('.corp-name-link')
        title = item.select_one('.information-title-link')
        body = item.select_one('.chip-information-group')
        relative_url = item.get('data-gavirturl')  


        data = {
            'Site': 'Job_Korea',
            'Col_company': company.get_text(strip=True) if company else None,
            'Col_Recruit': title.get_text(strip=True) if title else None,
            'Col_detail': body.get_text(strip=True) if body else None,
            'Col_url': relative_url
        }
        results.append(data)

    # 출력
    return pd.DataFrame(results)


def saramin_crawling():
    url = "https://www.saramin.co.kr/zf_user/search?searchword=데이터분석"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 결과 저장
    results = []

    # 각 공고 추출
    items = soup.select('div.item_recruit')

    for item in items:
        title_tag = item.select_one('h2.job_tit a')
        company_tag = item.select_one('strong.corp_name a')
        condition_tag = item.select_one('div.job_condition')

        # 변수 추출
        recruit_title = title_tag.text.strip() if title_tag else None
        company_name = company_tag.text.strip() if company_tag else None
        details = condition_tag.text.strip().replace('\n', ' ') if condition_tag else None
        recruit_url = urljoin(url, title_tag['href']) if title_tag else None

        # 저장
        results.append({
            'Site': 'Saramin',
            'Col_company': company_name,
            'Col_Recruit': recruit_title,
            'Col_detail': details,
            'Col_url': recruit_url
        })

    # 데이터프레임으로 변환
    return pd.DataFrame(results)






# ▶ Streamlit UI
def main():
    st.title("Title")

    if st.button("Recruit Searching"):
        df_jobkorea = Jobkorea_searching()
        
      
        df_saramin = saramin_crawling()

        df_all = pd.concat([df_jobkorea, df_saramin], ignore_index=True)
        st.dataframe(df_all)

        site_counts = df_all['Site'].value_counts()
        site_ratio = round((site_counts / site_counts.sum()) * 100, 2)
        
        
       
        df_summary = pd.DataFrame({
            'Site': site_counts.index,
            'Count': site_counts.values,
            'Ratio': site_ratio.values
        })

        
        st.dataframe(df_summary)

        # 파이 차트
        fig = px.pie(df_summary, values='Count', names='Site', title='Recruitment Ratio')
        st.plotly_chart(fig)

     

if __name__ == "__main__":
    main()
    
    
    
    
    