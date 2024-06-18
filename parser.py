import requests
from bs4 import BeautifulSoup
import asyncio
from utils.database import create_db
import utils.db_commands as db
from random import uniform, randint
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}

# response = requests.get("https://opensea.io/collection/nounishcnp", headers=headers)
# print(response.text)
# soup = BeautifulSoup(response.text, 'html.parser')
#


async def main():
    await create_db()
    links = ["https://opensea.io/collection/nounishcnp", "https://opensea.io/collection/cnp-students",
             "https://opensea.io/collection/10kworldcup", "https://opensea.io/collection/fluf",
             "https://opensea.io/collection/bullsandapes-genesis", "https://opensea.io/collection/coveredvillage",
             "https://opensea.io/collection/cel-mates-crime-reports", "https://opensea.io/collection/pecfriends",
             "https://opensea.io/collection/from-physical-to-digital", "https://opensea.io/collection/tubby-cats",
             "https://opensea.io/collection/cool-cats-nft"]

    desc = ["NounishCNP is a 3,333-piece collection starring CryptoNinja sub-characters. This is a fan art project of CNP and Nouns by NounsDAOJAPAN members.",
            "This NFT collection is fan art of CNP by YouthWeb3Lab StudentsCryptoNinja Partners Students (CNPS) is a 6,000 piece collection of CNP characters in various student forms.Students can become a CNPS holder and interact with the students! Adults, relive your school days and have some fun!",
            "10K World Cup is the first Social Game NFT collection for Sports fans all over the world. 200+ BAYC Captains have joined to cheer for their favorite teams",
            "Flufs are the collection that started it all. 10,000 3D rabbit avatars, programmatically-generated from over 270 traits! Unique by at least three degrees of separation, Flufs are yours to trade, collect and customise through our growing Scenes & Sounds collection.",
            "Bulls & Apes Project features fantastic 3D art, fleshed out tokenomics, fun gamification, and IRL events to reward holders. Holding NFTs in our collection gives you access to our private \"Inner Circle\" membership, which provides networking opportunities, masterminds, VC deal flow (for accredited investors), and more!",
            "-",
            "Crime reports are used to redeem Cel Mates and enter the hallowed halls of the Steel Hose Penitentiary. An exclusive hub for counterculture and creatives to gather",
            "PEC Friends is one of PECland's 3D collections of 9000 randomly generated and stylistically curated NFTs that exist on the Ethereum Blockchain. The free mint round supply is 1000. The second public round supply is 3000. The third public round supply is 5000. PECland is a web3 platform for people enjoying social party games.",
            "This are my Digital artwork. Because i am a graphic designer i love to play around with Photoshop, Illustrator, Procreate and more.",
            "bringing colour & creativity to the NFT space by supporting artists and spreading good vibes",
            "Cool Cats is a collection of 9,999 randomly generated and stylistically curated NFTs that exist on the Ethereum Blockchain. Cool Cat holders can participate in exclusive events such as NFT claims, raffles, community giveaways, and more. Remember, all cats are cool, but some are cooler than others."]
    i = 0
    for link in links:
        print(link)
        response = requests.get(link, headers=headers)

        description = desc[i]
        i += 1

        soup = BeautifulSoup(response.text, 'html.parser')
        name_collection = soup.find("h1", class_="iIKkrq").get_text()

        myspan = soup.find_all("span", class_="heRZSz")

        try:
            for item in myspan:
                name = item.get_text()
                my_test = soup.find_all('img', alt=name)
                link = my_test[1]['src']

                price = round(uniform(0.050, 2.0), 2)
                history_price = [round(uniform(price - 0.1, price + 0.1), 2) for i in range(0, 10)]

                await db.add_new_nft(name, link, name_collection, price,
                                     history_price, description, "Ethereum",
                                     randint(123, 432))
        except:
            pass
        await db.add_new_collection(name_collection)
        await asyncio.sleep(10)
asyncio.run(main())
