import os
import socket


# Calculate the edit distance of two string   
def EditDistanceRecursive(str1, str2):
    edit = [[i + j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                d = 0
            else:
                d = 1
            edit[i][j] = min(edit[i - 1][j] + 1, edit[i][j - 1] + 1, edit[i - 1][j - 1] + d)
    return edit[len(str1)][len(str2)]


# Calculate the similarity score of two string
def SimilarityScore(str1, str2):
    ED = EditDistanceRecursive(str1, str2)
    return round((1 - (ED / max(len(str1), len(str2)))) * 100, 2)


class Messenger:
    SocketSender = socket.socket()
    restore = []

    def __init__(self,restoreSeed) -> None:
        self.SocketSender = None
        self.restore = restoreSeed

    def DryRunSend(self,squence):  # send a sequence of messages (work for DryRun)
        #squence.display()  # Test only
        for message in squence.M:
            response = self.sendMessage(message)
            if response == "#error":
                return True
            squence.R.append(response)
        for message in self.restore.M:
            response = self.sendMessage(message)
            if response == "#error":
                return True
        return squence

    def ProbeSend(self,squence,index): # send a sequence of messages (work for Probe)
        for i in range(len(squence.M)):
            response = self.sendMessage(squence.M[i])
            if response == "#error":
                return "#error"
            elif response == '#crash':
                return '#crash'
            if i == index:
                res = response
        for i in range(len(self.restore.M)):
            resotreResponse = self.sendMessage(self.restore.M[i])
            if resotreResponse == "#error":
                return "#error"
            elif response == '#crash':
                return '#crash'
        return res

    def SnippetMutationSend(self,squence,index): # send a sequence of messages (work for SnippetMutate)
        for i in range(len(squence.M)):
            response = self.sendMessage(squence.M[i])
            if response == "#error":
                return "#error"
            elif response == '#crash':
                return '#crash'
            if i == index:
                res = response

        for i in range(len(self.restore.M)):
            resotreResponse = self.sendMessage(self.restore.M[i])
            if resotreResponse == "#error":
                return "#error"
            elif response == '#crash':
                return '#crash'

        pool = squence.PR[index]
        scores = squence.PS[index]
        #print("+++++")
        #print(res.strip())
        for i in range(len(pool)):
            c = SimilarityScore(pool[i].strip(), res.strip())
            #print(pool[i].strip())
            #print(str(c)+"   "+str(scores[i]))
            if c >= scores[i]:
                return ""
        return "#interesting-"+str(index)

    def sendMessage(self,message,time=0): # send a message
        if "IP" in message.headers and "Port" in message.headers:  # socket 
            ip = message.raw["IP"].strip()
            port =  int(message.raw["Port"])
            content =  message.raw["Content"]+"\r\n"

            try:
                self.SocketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #self.SocketSender.settimeout(5)
                self.SocketSender.connect((ip,port))
                #print("Content:"+content)  # Test only
                self.SocketSender.send(content.encode('utf8'))
                response = self.SocketSender.recv(1024).decode('utf8')
            except socket.timeout as e:
                if time < 3:   # repeat
                    self.sendMessage(self,message,time+1)
                else:
                    return "#crash"

            
            #print("Response:"+response)  # Test only
            return response
        else:
            print("Error : IP and Port of target should be included in input files")
            return "#error" # error


        