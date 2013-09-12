import sys, re, time
from grab import Grab

##########################################
# Main class
##########################################
class Main:
    DECKBOX_DOMAIN          = "http://deckbox.org"
    TRADE_TABLE_XPATH       = "//*[@id='content']/div[4]/div[2]/table/tr/td/div[1]/a[1]"
    TRADE_PAGINATION_XPATH  = "//*[@id='content']/div[4]/div[2]/div/div[1]/span"
    PAGINATION_LIMIT        = 15
    TIME_BETWEEN_REQUESTS   = 0.25 #in secondes
    OUTPUT_PADDING_SENT     = 10
    OUTPUT_PADDING_RECEIVED = 15

    def run(self, username):
        user_trades_url         = self.DECKBOX_DOMAIN + "/users/" + username + "/trades"
        trades_values           = []
        total_value_sent        = 0;
        total_value_received    = 0;
        total_pages             = 1;
        page_number             = 1;


        #TODO: get ride of this initial request to get the number of pages
        g = Grab()
        response = g.go(user_trades_url)

        try:
            total_trade_pages = re.search("(\d+)$", g.doc.select(self.TRADE_PAGINATION_XPATH).text()).group(1)
        except:
            print "Couldn't find user " + bcolors.FAIL + username + bcolors.ENDC
            return

        #Loop through each trades page to get the trades ID
        for page_number in range(1, int(total_trade_pages) + 1):

            #Limit the number of page to check
            if (page_number > self.PAGINATION_LIMIT):
                break

            print "Analysing url: " + user_trades_url + "?p1=" + str(page_number)
            g = Grab()
            response = g.go(user_trades_url + "?p1=" + str(page_number))

            #Check each trades link to get the trade id. Then request the trade page and get the sent value and received value
            for trade_link in g.doc.select(self.TRADE_TABLE_XPATH):
                trade_id = re.search("/trades/(\d+)", trade_link.attr('href')).group(1)
                user_id  = re.search("/trades/(\d+)\?s=(\d+)", trade_link.attr('href')).group(2)

                print "  Analysing trade : " + trade_id

                g = Grab()
                response = g.go(self.DECKBOX_DOMAIN + trade_link.attr('href'))

                trade_user_sent_value       = g.doc.select("//*[@id='trade']/div/div/table/tbody[contains(@id, '" + user_id + "')]/tr[last()]/td[last()]").text()
                trade_user_received_value   = g.doc.select("//*[@id='trade']/div/div/table/tbody[not(contains(@id, '" + user_id + "'))]/tr[last()]/td[last()]").text()
                trade_url = self.DECKBOX_DOMAIN + trade_link.attr('href')

                trades_values.append([trade_user_sent_value, trade_user_received_value, trade_url])
                time.sleep(self.TIME_BETWEEN_REQUESTS)

        print "\nVALUE SENT".rjust(self.OUTPUT_PADDING_SENT) + " " + "VALUE RECEIVED".rjust(self.OUTPUT_PADDING_RECEIVED)

        #Do the math
        for value_sent, value_received, trade_url in trades_values:

            try:
                converted_value_sent = float(value_sent[1:])
            except ValueError:
                converted_value_sent = 0

            try:
                converted_value_received = float(value_received[1:])
            except ValueError:
                converted_value_received = 0

            total_value_sent        += converted_value_sent
            total_value_received    += converted_value_received

            print self.get_colored_prices(converted_value_received, converted_value_sent, " (" + trade_url + ")")

        print "\nTOTAL RECEIVED".rjust(self.OUTPUT_PADDING_RECEIVED) + " " + "TOTAL SENT".rjust(self.OUTPUT_PADDING_SENT)
        print self.get_colored_prices(total_value_received, total_value_sent, " ($" + str(total_value_received - total_value_sent) + ")")

    #Method to get colorized values
    def get_colored_prices(self, value1, value2, append_string = ""):
        string = ""

        if (value1 > value2):
            string = bcolors.OKGREEN + ("$" + str(value1)).rjust(self.OUTPUT_PADDING_SENT) + bcolors.ENDC + " " + bcolors.FAIL + ("$" + str(value2)).rjust(self.OUTPUT_PADDING_RECEIVED) + bcolors.ENDC
        elif (value1 < value2):
            string = bcolors.FAIL + ("$" + str(value1)).rjust(self.OUTPUT_PADDING_SENT) + bcolors.ENDC + " " + bcolors.OKGREEN + ("$" + str(value2)).rjust(self.OUTPUT_PADDING_RECEIVED) + bcolors.ENDC
        else:
            string = ("$" + str(value1)).rjust(self.OUTPUT_PADDING_SENT) + " " + ("$" + str(value2)).rjust(self.OUTPUT_PADDING_RECEIVED)

        if (append_string):
            string += append_string

        return string

##########################################
# Class to handle terminal colors
##########################################
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

##########################################
if __name__ == "__main__":

    if (len(sys.argv) > 1):
        username = str(sys.argv[1])
    else:
        username = raw_input("Username: ")


    if (username.strip() == ""):
        print "You must specify a username"
        exit(0)

    program = Main()
    program.run(username.strip())
    exit(0)
