import requests
import lxml.html as html
import os
import datetime


HOME_URL = 'https://www.canyon.com/es-cl/bicicletas-de-carretera/bicicletas-carreras/ultimate/cf-sl/ultimate-cf-sl-8/2752.html?dwvar_2752_pv_rahmenfarbe=BK%2FBK'
XPATH_SECTION_TO_WATCH = '//div[@data-product-size="XS"]//div[@class="productConfiguration__availabilityMessage"]/text()'


def run():
    try:
        response = requests.get(HOME_URL)
        if response.status_code == 200:
            home = response.content.decode('utf-8')
            parsed = html.fromstring(home)
            section_to_watch = parsed.xpath(XPATH_SECTION_TO_WATCH)[0]
            section_to_watch = section_to_watch.strip()
            print(section_to_watch)

            if not os.path.isdir('logs'):
                os.makedirs('logs')

            now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f'logs/{now}.txt', 'w', encoding='utf-8') as f:
                f.write(section_to_watch)
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


if __name__ == '__main__':
    run()