import testbed.Testbed
import logging
import time

logger = logging.getLogger(__name__)

def run_test(testbed, num_experiment = 10, num_packet = 100, ipi = 100):
    #add a message in logs
    logger.info("Inizio script")

    #first flush initial output
    for n in testbed.activeNodes:
        n.flush()

    #wai a moment to give all node time to be ready
    time.sleep(.5)

    #do specified number of run
    for i in range(num_experiment):
        #in each run, do one send for each node
        for sender in testbed.activeNodes:
            #flush sender node output
            sender.flush()
            #send command to broadcast spcified number of packet with specified IPI
            sender.write(f"SEND ffff,{num_packet},{ipi}\n".encode('UTF-8'))
            #wait all packet are sent, plus .5s
            time.sleep(num_packet * ipi/1000.)

            #flush other nodes output
            for n in testbed.activeNodes:
                n.flush()
            #wait .5s to give time node ready
            time.sleep(.5)

    logger.info("Fine script")
