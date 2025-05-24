from playwright.sync_api import sync_playwright
from todoist_sync import sync_assignment
from dotenv import load_dotenv
import os
load_dotenv()
PASSWORD = os.getenv("USER_PASSWORD")

def remove_up_to_last(string, char):
    last_index = string.rfind(char)
    if last_index != -1:
        return string[last_index + 1:]  # Slice from the character after the last occurrence
    return string  # Return the original string if the character is not found

def get_assignments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # change to True once stable
        page = browser.new_page()

        # LOGIN FLOW
        page.goto("https://caryacademy.myschoolapp.com/app/student#login")
        page.fill('input[id="Username"]', "charlotte_lavin@caryacademy.org")
        page.click('#nextBtn')
        page.wait_for_url("https://login.microsoftonline.com/common/**")
        page.wait_for_load_state("networkidle")
        page.fill('input[id=i0118]', PASSWORD)
        page.click('#idSIButton9')
        page.click('#idBtn_Back')
        page.wait_for_url("**/progress")

        # Go to assignment center
        page.goto("https://caryacademy.myschoolapp.com/lms-assignment/assignment-center/student")
        page.wait_for_url("**/student")
        page.wait_for_load_state("networkidle")

        # 🧠 Grab all assignment links
        assignment_links = page.locator("a[href*='/lms-assignment/assignment/assignment-student-view/']").all()

        print(f"Found {len(assignment_links)} assignments.")

        for i, link in enumerate(assignment_links):
            try:
                href = link.get_attribute("href")
                if not href:
                    print(f"⚠️ Skipping link {i}, href is None")
                    continue

                print(f"✔️ Found link: {href}")
                page.goto("https://caryacademy.myschoolapp.com" + href)
                page.wait_for_load_state("networkidle")
                try: 
                    title = page.locator('//h1[contains(@class, "sky-font-heading-1")]/span').inner_text()
                except:
                    title = "Unknown"
                try:
                    class_name = page.locator('//dt[.//span[text()="Class"]]/following-sibling::dd[1]//span[contains(@class, "sky-description-list-description")]').inner_text()
                except:
                    class_name = "Unknown Class"
                due_date = page.locator('//dt[.//span[text()="Due"]]/following-sibling::dd[1]//span[contains(@class, "sky-description-list-description")]').inner_text().splitlines()[0]
                assignment_id = remove_up_to_last(href, "/")
                print(f"📚 {title} - {class_name} - {due_date}")

                assignment = {
                    "id": assignment_id,
                    "title": title,
                    "class_name": class_name,
                    "due_date": due_date,
                    "url": "https://caryacademy.myschoolapp.com" + href,
                }
                sync_assignment(assignment)
                # Go back to assignment list
                page.goto("https://caryacademy.myschoolapp.com/lms-assignment/assignment-center/student")
                page.wait_for_load_state("networkidle")

            except Exception as e:
                print(f"⚠️ Error extracting assignment from {href}: {e}")
                continue
