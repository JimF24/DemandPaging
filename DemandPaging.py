'''
JiaYi Feng
jf3354@nyu.edu
12.6.2018
Demand Paging
'''



import sys
import math

'''
Page class
@@@ param:
    pageNumber: page ID
    processNumber: process id
    loadTime
overrides __eq__ function to do comparisons.
'''
class Page:
    pageNumber = 0
    processNumber = 0
    loadTime = 0
    def __init__(self, pageN, proN):
        self.pageNumber = pageN
        self.processNumber = proN
    def __eq__(self, other):
        if(self.processNumber == other.processNumber) and self.pageNumber == other.pageNumber:
            return True
        else:
            return False

'''
Process class
@@@ param:
    processid
    size
    references: tracking remaining references
    number_of_evictions: tracking number of evictions to do final calculations
    number_of_PageFaults: tracking nubmer of page faults to do final calculations
    residency_time: tracking residency time to do final calculations
    number_of_references
    nextWord: calculate next word to load
    a: prob'y param
    b: prob'y param
    c: prob'y param
    first_reference = determine whether it's the first reference of this process or not
    
'''
class Process:
    processid = 0
    size = 0
    references = 0
    number_of_evictions = 0
    number_of_PageFaults = 0
    residency_time = 0
    number_of_references = 0
    nextWord = 0
    a = 0
    b = 0
    c = 0
    first_reference = True
    algorithm = None
    def __init__(self,processid,  a , b , c , num_of_references):
        self.processid = processid
        self.a = a
        self.b = b
        self.c = c
        self.number_of_references = num_of_references


def echo(machine,page,process,job,reference,algo):
    """

    :param machine: int
    :param page: int
    :param process: int
    :param job: int
    :param reference: int
    :param algo: string
    :return: None
    """
    print("The machine size is: ", machine)
    print("The page size is: ", page)
    print("The process size is: ", process)
    print("The job mix number is: ", job)
    print("The number of reerences per page is: ",reference)
    print("The algorithm that is used is: ",algo.upper())


def paging(machine_size, page_size,process_size,references, algo,randNum,processlist,RAM):
    """
    :param machine_size: int
    :param page_size: int
    :param process_size: int
    :param references: int
    :param algo: string
    :param randNum: file
    :param processlist: list of process objects
    :param RAM: list of pages
    :return: None
    """
    # maintain a page list
    pageList = []
    quantum = 3
    time = 1
    while time <= (len(processlist) - 1)*references:
        # loop through the process list
        for process in processlist:
            if process is not None:
                for i in range(quantum):
                    if process.number_of_references <= 0 :
                        break
                    word = 0
                    # if this is the first reference, assgin the word with (111*processid)%process_size
                    if process.first_reference:
                        word = (111 * process.processid) % process_size
                        process.nextWord = word
                        process.first_reference = False
                    else:
                        word = (process.nextWord + process_size) % process_size
                    # since page_number is an integer, use //
                    page_number = word // page_size
                    # create a page object with calculated page number and the processid of current process
                    cur_page = Page(page_number,process.processid)
                    frame_ind = -1
                    page_existed = False
                    # loop through RAM to find whether the page exists in RAM or not
                    for i in range(len(RAM)):
                        # if RAM contains the same page as the current page
                        if cur_page.__eq__(RAM[i]):
                            cur_page.loadTime = RAM[i].loadTime
                            frame_ind = i
                            page_existed = True
                            break
                    if not page_existed:
                        processlist[cur_page.processNumber].number_of_PageFaults += 1
                    if frame_ind >= 0:
                        # if the algo is LRU, we should rearrange the page in the page list since it is hit and most recently used.
                        if algo.upper() == "LRU":
                            if cur_page in pageList:
                                pageList = [page for page in pageList if not page.__eq__(cur_page)]
                                pageList.append(cur_page)
                    # else, it is a new page, whehter put it in RAM or evict an existed page
                    else:
                        possibly_evicted_frame = -1
                        # we have free space in RAM, put the current page in RAM
                        if len(RAM) < machine_size/page_size:
                            RAM.insert(0,cur_page)
                            pageList.append(cur_page)
                            cur_page.loadTime = time
                            for i in range(len(RAM)):
                                if cur_page.__eq__(RAM[i]):
                                    possibly_evicted_frame = i
                        # no free space, select a frame to be evicted
                        elif algo.upper() == "LRU":
                            page_to_remove = pageList.pop(0)
                            for page in RAM:
                                if page.__eq__(page_to_remove):
                                    processlist[page_to_remove.processNumber].number_of_evictions += 1
                                    RAM[RAM.index(page)] = cur_page
                                    cur_page.loadTime = time
                                    processlist[page_to_remove.processNumber].residency_time += time - page_to_remove.loadTime
                                    pageList.append(cur_page)
                                    possibly_evicted_frame = RAM.index(cur_page)
                                    break
                        elif algo.upper() == "LIFO":
                            page_to_remove = pageList.pop()
                            for page in RAM:
                                if page.__eq__(page_to_remove):
                                    processlist[page_to_remove.processNumber].number_of_evictions += 1
                                    RAM[RAM.index(page)] = cur_page
                                    cur_page.loadTime = time
                                    processlist[page_to_remove.processNumber].residency_time += time - page_to_remove.loadTime
                                    pageList.append(cur_page)
                                    possibly_evicted_frame = RAM.index(cur_page)
                                    break
                        elif algo.upper() == "RANDOM":
                            rand_victim = int(int(next(randNum)) %  int((machine_size/page_size)))
                            page_to_remove = RAM[rand_victim]
                            processlist[page_to_remove.processNumber].number_of_evictions += 1
                            processlist[page_to_remove.processNumber].residency_time += time - page_to_remove.loadTime
                            RAM[rand_victim] = cur_page
                            cur_page.loadTime = time
                            possibly_evicted_frame = rand_victim
                    # determine the next word depending on random numbers
                    next_random = int(next(randNum))
                    y = next_random / 2147483648
                    if y < process.a:
                        process.nextWord = (process.nextWord+1) % process_size
                    elif y < process.a + process.b:
                        process.nextWord = (process.nextWord - 5) % process_size
                    elif y < process.a + process.b + process.c:
                        process.nextWord = (process.nextWord + 4) % process_size
                    else:
                        next_random_int = int(next(randNum))
                        process.nextWord = next_random_int % process_size
                    process.number_of_references -= 1
                    time += 1
    # final calculations for outputs
    total_page_faults = 0
    total_evictions = 0
    average_residency_time = 0
    for process in processlist:
        if process is not None:
            total_page_faults += process.number_of_PageFaults
            total_evictions += process.number_of_evictions
            average_residency_time += process.residency_time
            if process.number_of_evictions == 0:
                print("Process ",process.processid, " had ", process.number_of_PageFaults, " page faults with no evictions, so the average residence time is undefined")
            else:
                print("Process ", process.processid, " had", process.number_of_PageFaults, " page faults and ", process.residency_time/process.number_of_evictions, " average residency")

    if total_evictions == 0:
        print("The total number of page faults is", total_page_faults,", with no evictions, the overall average residency time is undefined")
    else:
        average_residency_time = average_residency_time/total_evictions
        print("The total number of page faults is", total_page_faults," and the overall average residency time is", average_residency_time)





def main():
    RAM = []
    process_list = [None]
    machine_size = int(sys.argv[1])
    page_size = int(sys.argv[2])
    process_size  = int(sys.argv[3])
    job_mix = int(sys.argv[4])
    references = int(sys.argv[5])
    algo = sys.argv[6]
    randomNumbers = open("random-numbers")
    if job_mix == 1:
        process_list.append(Process(1,1,0,0,references))
    elif job_mix == 2:
        for i in range(1,5):
            process_list.append(Process(i,1,0,0,references))
    elif job_mix == 3:
        for i in range(1,5):
            process_list.append(Process(i,0,0,0,references))
    elif job_mix == 4:
        process_list.append(Process(1,0.75,0.25,0,references))
        process_list.append(Process(2,0.75,0,0.25,references))
        process_list.append(Process(3,0.75,0.125,0.125,references))
        process_list.append(Process(4,0.5,0.125,0.125,references))
    echo(machine_size, page_size,process_size,job_mix,references,algo)
    paging(machine_size, page_size, process_size , references, algo, randomNumbers, process_list, RAM )
main()

