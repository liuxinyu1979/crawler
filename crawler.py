import ggzyCrawler
import os
import sys, getopt

def usage():
    print ("\t\t\t********** Help Menu **********\t\t\t")
    print ("python3 crawler.py <option list> ")
    print ("-h Print help menu")
    print ("-p populate the historical data")
    print ("-d daily crawl")
    print ("-s computes summary")
    print ("examples:")
    print ("example1 : python3 crawler.py -i")
    print ("example2 : python3 crawler.py -d")
    exit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append('-?')
    ggzy_crawler = ggzyCrawler.GGZYCralwer('http://ggzy.gz.gov.cn/jyywjsgcfwjzzbgg/index.jhtml')

    try :
        optList, args = getopt.getopt(sys.argv[1:], 'd?p')
        for k, v in optList:
            if k == '-?':
                os.system('clear')
                print (usage())
            elif k == '-p':
                ggzy_crawler.crawl_historical_data()
            elif k == '-d':
                ggzy_crawler.crawl_for_the_day()
            elif k == '-s':
                ggzy_crawler.compute_summary()                
            else:
                raise getopt.GetoptError(k + ":" + v)
    except getopt.GetoptError as err:
        os.system('clear')
        print ("\t*** unexpected input argument received: " + str(err))
        print (usage())

