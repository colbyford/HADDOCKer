"""
for the setup of the queuing system you may want to change the
variable:
useLongJobFileNames = 1 #default
to:
useLongJobFileNames = 0

the .job files are started with (if useLongJobFileNames = 1):
queue_1 /home/Bis/linge/werner1.1_run3_it0_refine_18.job
where queue_1 is set in the run.cns file

for useLongJobFileNames = 0 it will look like:
queue_1 werner1.1_run3_it0_refine_18.job

"""
# = 1 means e.g. "/home/Bis/linge/werner1.1_run3_it0_refine_18.job"
# = 0 means e.g. "werner1.1_run3_it0_refine_18.job"
useLongJobFileNames = 0 

