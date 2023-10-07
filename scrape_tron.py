import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import requests
import json
from selenium.common.exceptions import NoSuchElementException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Edge(options=chrome_options)
wait = WebDriverWait(driver, 100)
# Fungsi untuk melakukan scraping dan mengirim hasil ke server
def scrape_and_send_results(contract_address):
    try:

        driver.get('https://tronscan.org/#/tools/code-reader?')

        # Tunggu hingga tombol "I Understand" muncul (dengan waktu maksimum 10 detik)
        understand_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button/span[contains(text(),"I Understand")]'))
        )

        # Klik tombol "I Understand"
        understand_button.click()
        
        # Cari elemen input berdasarkan ID
        input_element = driver.find_element(By.ID,'form_key')

        # Masukkan teks ke dalam input
        input_element.send_keys('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')

        input_element = driver.find_element(By.CSS_SELECTOR,'input[placeholder="Contract Address"]')
        input_element.send_keys(contract_address)

        load_button = driver.find_element(By.CLASS_NAME,'ant-btn-primary')
        load_button.click()
        time.sleep(5)


        if driver.find_element(By.CSS_SELECTOR,'#form > div.select-contract-file-wrapper > div.fileContractSelect'):
            file_contract_select = driver.find_element(By.CLASS_NAME,'#form > div.select-contract-file-wrapper > div.fileContractSelect')

                # Temukan semua elemen input checkbox dalam elemen "fileContractSelect"
            checkbox_inputs = file_contract_select.find_element(By.CSS_SELECTOR,'input[type="checkbox"]')

                # Loop melalui setiap input checkbox dan klik
            for i in range(1, len(checkbox_inputs)):
                checkbox_inputs[i].click()

            time.sleep(20)
                # Tunggu hingga textarea muncul (dengan waktu maksimum 10 detik)
            textarea_wrapper = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'textarea-wrapper'))
            )

                # Temukan textarea di dalam wrapper
            textarea_element = textarea_wrapper.find_element(By.TAG_NAME, 'textarea')

                # Masukkan data string ke dalam textarea
            data_string = 'Please make condition(yes/no) of each answer, Only with this format : "yes/no - explanation", I have 18 questions: 1. Does the Contract have a hidden owner?  ; 2. Does the contract have an admin privileges?  ; 3. Does the Contract look like a honeypot?  ; 4. Does the Contract Owner can change the balance token?  ; 5. Does the contract is proxy contract?  ; 6. Does the Contract have a whitelist?  ; 7. Does the Contract have a blacklist?  ; 8. Does the slippage can be modified on contract?  ; 9. Does the contract can take back ownership?  ; 10. Does the contract have a trading-cool-down mechanism?  ; 11. Does the contract can mint new tokens?  ; 12. Does the contract can burn the tokens?  13. Does the contract upgradeable?  14. Does the contract can be paused?  15. Does the contract have a cooldown feature?  16. Does the contract can establish or update Fees?  17. Does the contract was hardcoding addresses?  18. Does the contract use many functions that can only be called by the owner?  "notes: please make sure the answer aaccording to what is in the contract. *(Say "yes" if "the contract does" AND TELL US WHERE THE CODE IS LOCATED, Say "no" if "the contract does not") *(Dont repeat question)'

            textarea_element.send_keys(data_string)

                # Temukan elemen tombol "Submit" dan klik
            submit_button = textarea_wrapper.find_element(By.CLASS_NAME, 'submit-btn')
            submit_button.click()
            time.sleep(30)

            dialogue_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="dialogue-wrapper"]//div[@class="dialogue"]'))
            )
                # Mengambil teks dari elemen dialogue
            dialogue_text = dialogue_element.text

            matches_array = re.split(r'\n', dialogue_text)

                # Membersihkan spasi ekstra di setiap elemen array
            matches_array = [match.strip() for match in matches_array if match.strip()]

                # Batasan jumlah nilai yang diinginkan (18)
            desired_count = 18
            final_matches_array = []

                # Memproses nilai-nilai hingga mencapai jumlah yang diinginkan
            for match in matches_array:
                final_matches_array.append(match)
                if len(final_matches_array) >= desired_count:
                    break

            print(final_matches_array)
            all_data = {
                'matches': final_matches_array
            }
        else:
            all_data = {
                'matches': ["This contract is not open source, we cannot scan its inner workings. Therefore, you should be extra careful with these tokens, as the lack of open source code in the contract is an indication of Fraud Token"]
            }
        server_url = 'http://localhost:5000/api/contract/matches'
        requests.post(server_url, json=all_data)


    except Exception as e:
        print("Tidak dapat menemukan elemen input atau mengirim teks ke dalamnya.", e)

    finally:
        driver.quit()  # Tutup WebDriver setelah selesai

if __name__ == '__main__':
    if len(sys.argv) > 1:
        contract_address = sys.argv[1]
        scrape_and_send_results(contract_address)