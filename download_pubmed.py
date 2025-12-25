r"""
Python script to download PubMed `N_max` articles abstracts for a user's specified period
  Example to run this conversion script:
    python download_pubmed.py \
     --output_json $PATH_TO_JSON_FILE
     --num_articles 1000 \
     --start_date "2023/11/01" \
     --end_date "2023/11/30"

"""
from argparse import ArgumentParser
import time

from Bio import Entrez
import json


def search(query, max_num_articles):
    "Retrieve the ids of first `max_num_articles` based on the provided query"
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax=max_num_articles,
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    """
    Fetch the metadata of PubMed articles based on their IDs
    """
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pubmed', 
                        retmode='xml', 
                        id=ids)
    results = Entrez.read(handle)
    return results


def get_pubmed_data(
    output_json_file: str, 
    start_date: str = "2023/12/1",
    end_date: str = "2025/12/31",
    email: str = '25125080@bjtu.edu.cn', 
    max_num_articles: int = 20000
):
    """
    Download the first `max_num_articles` pubmed abstracts published between `start_date` and `end_date`
    
    Parameters: 
    ----------
    output_json_file: Path to the JSON file where to store the downloaded articles
    start_date: Start date, in the format of "%Y/%m/%d", for the PubMed article search based on their publication date.
    end_date: End date for, in the format of "%Y/%m/%d", the PubMed articles search based on their publication date.
    """
    # Always provide your email when using Entrez
    Entrez.email = email

    # Format the date range in YYYY/MM/DD format for the query
    query = f"({start_date}[Date - Publication] : {end_date}[Date - Publication])"
    start_time = time.time()
    # Search for articles
    results = search(query, max_num_articles=max_num_articles)
    id_list = results['IdList']

    # Fetch details of retrieved articles
    papers = fetch_details(id_list)
    
    # Retrieve titles, dates and abstracts. 
    # Keep only articles where date and abstract information is available
    result = {}
    pubmed_articles = papers.get('PubmedArticle', [])
    
    for i, paper in enumerate(pubmed_articles):
        try:
            # 1. 安全提取标题
            medline = paper.get('MedlineCitation', {})
            article = medline.get('Article', {})
            title = article.get('ArticleTitle', 'No Title')
            
            # 2. 安全提取摘要 (这是 RAG 的核心)
            abstract_data = article.get('Abstract', {})
            abstract_text_list = abstract_data.get('AbstractText', [])
            if not abstract_text_list:
                continue # 没有摘要就跳过这一篇
            
            # 将可能的列表合并为字符串
            abstract_text = " ".join([str(text) for text in abstract_text_list])
            
            # 3. 安全提取日期 (优先找 ArticleDate，没有就找 Journal 里的 PubDate)
            art_date_list = article.get('ArticleDate', [])
            if art_date_list:
                year = art_date_list[0].get('Year', '2024')
                month = art_date_list[0].get('Month', '01')
                day = art_date_list[0].get('Day', '01')
            else:
                # 备选：从期刊发行信息里拿年份
                journal_issue = article.get('Journal', {}).get('JournalIssue', {})
                pub_date = journal_issue.get('PubDate', {})
                year = pub_date.get('Year', '2024')
                month = pub_date.get('Month', '01')
                day = '01'

            # 4. 存入结果
            result[len(result)] = {
                "article_title": title,
                "article_abstract": abstract_text,
                "pub_date": {"year": year, "month": month, "day": day}
            }
            
            # 达到数量上限就停止
            if len(result) >= max_num_articles:
                break
                
        except Exception as e:
            # 遇到单篇解析错误，跳过，不影响整体
            continue
    # 将结果保存到指定的 JSON 文件中
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(
            list(result.values()), 
            f, 
            ensure_ascii=False, 
            indent=4
        )
    print(f"数据已成功写入到文件: {output_json_file}")

    print(f"成功保存了 {len(result)} 篇带有摘要的文章。")
        

def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--output_json",
        type=str,
        default=None,
        required=True,
        help="Path to the JSON file where to store the downloaded articles",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        required=True,
        help="Start date for the PubMed search",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        default=None,
        required=True,
        help="End date for the PubMed search",
    )
    parser.add_argument(
        "--num_articles",
        type=int,
        default=1000,
        help="The numer of articles to retrieve from the PubMed search query",
    )
    #num_articles
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    get_pubmed_data(output_json_file=args.output_json, start_date=args.start_date, end_date=args.end_date, max_num_articles=args.num_articles)
