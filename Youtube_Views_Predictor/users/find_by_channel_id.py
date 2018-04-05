import json

import datetime

import psycopg2
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
# driver1 = webdriver.Firefox()
url = "https://socialblade.com/youtube/top/5000"
# driver1.get(url)
# output_file = open('youtube_data_' + str(datetime.datetime.now().strftime('%H_%M_%S')) + '.json', 'w', encoding='utf-8')
# final_data = []
conn = psycopg2.connect(database="yvp4", user="postgres", password="harshit24")
cur = conn.cursor()


def get_block(channel_id,id):
    driver2 = webdriver.Chrome()
    get_more_data(channel_id,id,driver2)
    driver2.close()

def check_or_update_channel_main(channelid, category,driver2,id):
    print("in check or update")
    cur.execute("SELECT * from users_user_channel_main where id='" + str(id) + "'")
    check_data = cur.fetchone()
    print(check_data[1])
    print(check_data[2]=='')
    if check_data[2] == '':
        #try:
        print('inif')
        imgurl = (driver2.find_element_by_xpath('//*[@id="YouTubeUserTopInfoAvatar"]').get_attribute('src'))
        cur.execute(
            "UPDATE users_user_channel_main SET channel_image_url='{0}',category = '{1}' WHERE id='{2}'".format(
                imgurl, category, id))
        '''except Exception as e:
        #    print("error while entring in db ", e)
        '''
        conn.commit()


def get_more_data(channel_id,id,driver2):
    new_url = 'https://socialblade.com/youtube/channel/' + str(channel_id) + '/monthly'
    driver2.get(new_url)
    time.sleep(10)
    try:
        channeltype = driver2.find_element_by_xpath('//*[@id="youtube-user-page-channeltype"]').text
    except NoSuchElementException:
        channeltype = "Not Available"
    try:
        for i in range(5, 35):
            #try:
            block = driver2.find_element_by_xpath('/ html / body / div[10] / div[2] / div /div[1] / div[' + str(i) + ']')
            #except NoSuchElementException:
            #block = driver2.find_element_by_xpath('/ html / body / div[16] / div / div[1] / div[' + str(i) + ']')
            try:
                date_tag = block.find_element_by_xpath('div[1]')
                subscribers_tag = block.find_element_by_xpath('div[3]/div[2]')
                subscribers = (subscribers_tag.text).replace(",", "")
                video_views_tag = block.find_element_by_xpath('div[4]/div[2]')
                video_views = (video_views_tag.text).replace(",", "")
                insert_in_channel_sub(id, date_tag.text, subscribers, video_views)
            except NoSuchElementException:
                continue
        check_or_update_channel_main(channel_id,channeltype,driver2,id)

        '''final_data.append({
                'channel_id': channelid,
                'channel_type': channeltype,
                'date': date_tag.text,
                'subscribers': subscribers,
                'video_views': video_views
            })'''
        '''
       except NoSuchElementException:
        print("in Except")
        count = 0
        try:
            otherlink_tag = driver2.find_element_by_xpath('/html/body/div[10]/div[2]/div/h2/a')
            url2 = otherlink_tag.get_attribute('href')
            print(url2)
            driver2.get(url2)
            driver2.implicitly_wait(5)
            cur.execute("UPDATE channel_channel_main SET social_url='{0}' WHERE id='{1}'".format(driver2.current_url,
                                                                                                 channelid))
            conn.commit()
            new_url = driver2.current_url + "/monthly"
            driver2.get(new_url)
            channeltype = driver2.find_element_by_xpath('//*[@id="youtube-user-page-channeltype"]').text
            for i in range(34,4):
                try:
                    block = driver2.find_element_by_xpath(
                        '/ html / body / div[15] / div / div[1] / div[' + str(i) + ']')
                except NoSuchElementException:
                    block = driver2.find_element_by_xpath(
                        '/ html / body / div[16] / div / div[1] / div[' + str(i) + ']')
                try:
                    date_tag = block.find_element_by_xpath('div[1]')
                    subscribers_tag = block.find_element_by_xpath('div[3]/div[2]')
                    subscribers = (subscribers_tag.text).replace(",", "")
                    video_views_tag = block.find_element_by_xpath('div[4]/div[2]')
                    video_views = (video_views_tag.text).replace(",", "")
                    print("count", count)
                    if count <3:
                        insert_in_channel_sub(channelid, date_tag.text, subscribers, video_views)
                except NoSuchElementException:
                    continue
                final_data.append({
                    'channel_id': channelid,
                    'channel_type': channeltype,
                    'date': date_tag.text,
                    'subscribers': subscribers,
                    'video_views': video_views
                })
            check_or_update_channel_main(channelid, channeltype)
        except Exception as e:
            print("inner unknown error", e)
        '''
    except Exception as e:
        print("outer unknown error", e)


def insert_in_channel_sub(id, date, subscriber_count, view_count):
    cur.execute("SELECT * FROM users_user_channel_sub WHERE date1='{0}' AND channel_id_id='{1}'".format(date, id))
    check = cur.fetchone()
    if check is None:
        cur.execute(
            "INSERT INTO users_user_channel_sub (channel_id_id, date1, view_count, subscriber_count) VALUES ('{0}','{1}','{2}','{3}')".format(
                id, date, view_count, subscriber_count))

        print("data added in channel_channel_sub table")
    else:
        cur.execute(
            "UPDATE users_user_channel_sub SET view_count='{0}', subscriber_count='{1}' WHERE channel_id_id='{2}' AND date1='{3}'".format(
                view_count, subscriber_count, id, date)
        )
        print("data already there in channel_channel_sub table")
    conn.commit()

#get_block("UCRijo3ddMTht_IHyNSNXpNQ")
# write()
# output_file.close()
# driver1.close()

