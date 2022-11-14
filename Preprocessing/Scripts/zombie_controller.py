import subprocess
from subprocess import check_output
import traceback
import time

def find_and_kill():
    try:
        #   Launch the command for get the zombies
        #p1 = subprocess.Popen(["top","-b1","-n1"] , stdout=subprocess.PIPE)
        #p2 = subprocess.Popen(["grep","S"] , stdin=p1.stdout)
        #p1 = check_output(["top","-b1","-n1|grep","S"])
        #p2 = check_output(["grep","Z"], stdin=p1.stdout)
        #strings = p2.splitlines()
	
        out = subprocess.getoutput('top -b1 -n1 | grep Z')
	
        if len(out) > 0:
            strings = out.splitlines()
	    #   saltare le prime 2 righe
            for s in strings[2:]:
                #print(str(s).split())
                process =  s.split()
                if "Z" in process:
                    print("Zombie find: ",process)
		            #kill the zombie
                    print("PID: ",process[1])
                    p1 = subprocess.Popen(["kill","-9",process[0]] , stdout=subprocess.PIPE)
		    
    except Exception:
        print("Errore ...")
        traceback.print_exc()



if __name__ == "__main__":

    print("Start find and kill all zombies !")

    while True:
        
        find_and_kill()
        #ogni 15 secondi
        time.sleep(15)
