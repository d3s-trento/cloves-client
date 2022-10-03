import re, numpy
from pathlib import Path
from collections import namedtuple

from deploymentMap import idByAddr

A = {'16MHz' : 113.77, '64MHz' : 121.74}
prf = '64MHz'

Conf = namedtuple('Configuration', 'channel PRF PLEN PAC preamble_code SFD data_rate PHR sfd_timeout',
                  defaults=[None,]*9)

Link = namedtuple('Link', ['src', 'dest', 'conf'])

Packet = namedtuple('Packet', 'src dest seqn first_path_strength received_strength')

def parseFile(inputFilePath):

    serialLogPattern = re.compile(r'\[?(?P<timestamp>[\d-]+\s[\d:,]+)\]?\s[\w:.]+\s(?:-\s)?(?P<nodeId>\d+).(?P<board>\w+)\s[<>]\s(?P<message>.*)$')
    
    configPattern = [re.compile(r"DW1000 Radio Configuration: "),
                     ('channel',re.compile(r"Channel: (\d+)")),
                     ('PRF',re.compile(r"PRF: (.*)")),
	             ('PLEN',re.compile(r"PLEN: (\d*)")),
	             ('PAC',re.compile(r"PAC Size: (\d*)")),
	             ('preamble_code',re.compile(r"Preamble Code: (\d*) (\d*)")),
	             ('SFD',re.compile(r"SFD: (\d*)")),
	             ('data_rate',re.compile(r"Data Rate: (.*)")),
	             ('PHR',re.compile(r"PHR Mode: (.*)")),
	             ('sfd_timeout',re.compile(r"SFD Timeout: (\d*)"))
    ]

    sendTestPattern = re.compile("send test from node: ([0-9a-fA-F]{4}) to \[(.*)\]")
    sendCmdPattern = re.compile("SEND ([0-9a-f]{4}),(\d+),(\d+)")

    rangeTestPattern = re.compile("range test from node: ([0-9a-fA-F]{4}) to \[(.*)\]")
    rangeCmdPattern = re.compile("RANGE (?P<peer>[0-9a-fA-F]{4}),(?P<nPacket>\d*),(?P<ipi>\d*)")

    receivedPatt = re.compile('received \[(?P<src>.*)-(?P<dst>.*)\] seqn (?P<seqn>\d+), (\d+) (\d+) (\d+) (\d+) (\d+)')
    rangePatt = re.compile('range \[(.*)-(.*)\]: (?P<range>-?\d*) bias (?P<bias>-?\d*)')

    lastConfigs = {}

    sendTests = []

    with inputFilePath.open() as fin:
        for logLine in fin:

            lm = serialLogPattern.match(logLine)
            if lm is None:
                #print(f"not logLine '{logLine[:-1]}'")
                continue
        
            m = sendCmdPattern.search(lm.group('message'))
            if m is not None:
                #send command line
                if m.group(1) !=  'ffff':
                    print("send test not on broadcast")
                    exit(1)

                nPacket = int(m.group(2))
                pkts = {}

                src = int(lm.group('nodeId'))
                sendTests.append({'src':src, 'conf': lastConfigs.get(src), 'nPackets':nPacket, 'pkts':pkts})
                #print(f"nPacket: {nPacket}")
                continue

            m = receivedPatt.search(lm.group('message'))
            if m is not None:
                if False: #m.group('src') != lastSendTest[1][0]:
                    print(f"Packet in wrong test: '{l}'")
                else:
                    vals = list(map(int, (m.group(4), m.group(5), m.group(6), m.group(7), m.group(8))))
                    if 0 in vals[4:5]:
                        print(f"0 in line '{logLine}'")                        
                    else:
                        
                        fpl = 10 * numpy.log10((vals[0]**2 + vals[1]**2 + vals[2]**2) / vals[4]**2) - A[prf]
                        rxl = 10 * numpy.log10((vals[3] * 2**17) / vals[4]**2) - A[prf]
                        
                        dest = idByAddr[m.group('dst')]
                        if dest not in sendTests[-1]['pkts']:
                            sendTests[-1]['pkts'][dest] = list()
                        
                        sendTests[-1]['pkts'][dest].append(Packet(idByAddr[m.group('src')], dest,
                                                                  int(m.group('seqn')), fpl, rxl))
                continue

            m = configPattern[0].search(lm.group('message'))
            if m is not None:
                config = dict()
                for p in configPattern[1:]:
                    l = fin.readline()
                    m = p[1].search(l)
                    if m is None:
                        print(f"Not matching config line: {l}")
                        exit(1)

                    lastConfigs[int(lm.group('nodeId'))] = Conf(**config)
                continue

    return sendTests

def agregateLink(sendTests):
    """
    This function will elaborate sendTests from parse file and will reorganize data by link
    """
    links_data = {}

    for st in sendTests:
        for dest, vals in st['pkts'].items():
            link = Link(src= st['src'], dest= dest, conf=st['conf'])
            if link not in links_data:
                links_data[link] = {'experiments': list()}

            links_data[link]['experiments'].append({'nPackets':st['nPackets'],
                                                    'vals': vals})

    return links_data

def computeLinkStatistick(links):
    for link, data in links.items():
        

        expectedPackets = 0
        receivedPackets = 0
        sumFpl = 0
        sumFpl2 =0
        sumRxl = 0
        sumRxl2 = 0
         
        for e in data['experiments']:
            expectedPackets += e['nPackets']
            receivedPackets += len(e['vals'])

            for p in e['vals']:
                sumFpl += p.first_path_strength
                sumFpl2 += p.first_path_strength**2
                sumRxl += p.received_strength
                sumRxl2 += p.received_strength**2


        fpl_avg = sumFpl / receivedPackets
        fpl_std = numpy.sqrt((sumFpl2 / receivedPackets)- fpl_avg**2)
        
        rxl_avg = sumRxl / receivedPackets
        rxl_std = numpy.sqrt((sumRxl2 / receivedPackets)- rxl_avg**2)
                
        data['statistics'] = {'nExperiments': len(data['experiments']),
                              'totExpectedPackets': expectedPackets,
                              'pdr': receivedPackets / expectedPackets,

                              'fpl_avg': fpl_avg,
                              'fpl_std': fpl_std,

                              'rxl_avg': rxl_avg,
                              'rxl_std': rxl_std,
                              }
        
if __name__ == '__main__':
    
    import argparse

    cliParser = argparse.ArgumentParser()
    cliParser.add_argument('inputFile', help="file to be elaborated")
    cliParser.add_argument('outputCsv', help="name of the output file")

    args = cliParser.parse_args()

    sendData = parseFile(Path(args.inputFile))

    #print(sendData)

    links = agregateLink(sendData)

    computeLinkStatistick(links)

    import csv
    fieldnames=['src', 'dest', 'conf','nExperiments', 'totExpectedPackets','pdr',
                'fpl_avg', 'fpl_std', 'rxl_avg', 'rxl_std']

    with open(args.outputCsv, 'w') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for l in sorted(links):
            writer.writerow({**l._asdict(), **links[l]['statistics']})
            #print(f"link {l}: {links[l]['statistics']}")
    
