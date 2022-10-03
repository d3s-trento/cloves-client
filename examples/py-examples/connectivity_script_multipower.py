import testbed.Testbed
import logging
import time

logger = logging.getLogger(__name__)

def run_test(testbed):
    logger.info("Inizio script")

    num_packet = 100
    ipi = 100
    powers = [0, 165, 335] #0dB, 16.5dB, 33.5dB

    #first flush initial output
    for n in testbed.activeNodes:
        n.flush()

    time.sleep(.5)
    
    for p in powers:
        #configure all nodes
        for n in testbed.activeNodes:
            n.write(f"SET_POWER 0,{p}\n".encode('UTF-8'))
            time.sleep(.1)
            n.write("COMMIT\n".encode('UTF-8'))
            n.flush()

        time.sleep(.5)
    
        for sender in testbed.activeNodes:
            sender.flush()
            sender.write(f"SEND ffff,{num_packet},{ipi}\n".encode('UTF-8'))
            time.sleep(num_packet * ipi/1000. + .5)
            for n in testbed.activeNodes:
                n.flush()
        time.sleep(.5)
            
    logger.info("Fine script")
