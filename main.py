from dotenv import load_dotenv
from scrape_jobs import *

load_dotenv()

"""
List of countries url.
"""
nigeria = 'https://ng.indeed.com'
united_kingdom = 'https://uk.indeed.com'
united_states = 'https://www.indeed.com'
canada = 'https://ca.indeed.com'
germany = 'https://de.indeed.com'
australia = 'https://au.indeed.com'
south_africa = 'https://za.indeed.com'
sweden = 'https://se.indeed.com'
singapore = 'https://www.indeed.com.sg'
switzerland = 'https://www.indeed.ch'
united_arab_emirates = 'https://www.indeed.ae'
new_zealand = 'https://nz.indeed.com'
india = 'https://www.indeed.co.in'
france = 'https://www.indeed.fr'
italy = 'https://it.indeed.com'
spain = 'https://www.indeed.es'
japan = 'https://jp.indeed.com'
south_korea = 'https://kr.indeed.com'
brazil = 'https://www.indeed.com.br'
mexico = 'https://www.indeed.com.mx'
china = 'https://cn.indeed.com'
saudi_arabia = 'https://sa.indeed.com'
egypt = 'https://eg.indeed.com'
thailand = 'https://th.indeed.com'
vietnam = 'https://vn.indeed.com'
argentina = 'https://ar.indeed.com'
ireland = 'https://ie.indeed.com'

def main():
    driver = configure_webdriver()
    country = india
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("PASSWORD")
    job_position = 'web developer'
    job_location = 'remote'
    date_posted = 20

    cleaned_df = None

    try:
        full_url = search_jobs(driver, country, job_position, job_location, date_posted)
        check_for_captcha(driver)  # Check for CAPTCHA
        df = scrape_job_data(driver, country)

        if df.shape[0] == 1:
            print("No results found. Something went wrong.")
            subject = 'No Jobs Found on Indeed'
            body = """
            No jobs were found for the given search criteria.
            Please consider the following:
            1. Try adjusting your search criteria.
            2. If you used English search keywords for non-English speaking countries,
               it might return an empty result. Consider using keywords in the country's language.
            3. Try more general keyword(s), check your spelling or replace abbreviations with the entire word

            Feel free to try a manual search with this link and see for yourself:
            Link {}
            """.format(full_url)

            send_email_empty(sender_email, receiver_email, subject, body, password)
        else:
            cleaned_df = clean_data(df)
            csv_file = save_csv(cleaned_df, job_position, job_location)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            if cleaned_df is not None:
                send_email(cleaned_df, sender_email, receiver_email, job_position, job_location, password)
        except Exception as e:
            print(f"Error sending email: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    main()