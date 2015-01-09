from flask import Flask
import boto.swf.layer2 as swf
from boto.swf.exceptions import SWFTypeAlreadyExistsError, SWFDomainAlreadyExistsError
import redis,time, logging, os, binascii
r = redis.StrictRedis(host='tes-pu-3jpt4w8eifgu.qpeias.0001.usw2.cache.amazonaws.com', port = 6379, db=0)
logging.basicConfig(filename='/var/log/edge/edge.log',level=logging.INFO)

swf_domain= 'demo'
VERSION='1.0'
registerables = []
registerables.append(swf.Domain(name=swf_domain))
app = Flask(__name__)

for workflow_type in ('HelloWorkflow', 'SerialWorkflow', 'ParallelWorkflow', 'SubWorkflow'):
    registerables.append(swf.WorkflowType(domain=swf_domain, name=workflow_type, version=VERSION, task_list='default'))

for activity_type in ('HelloWorld', 'ActivityA', 'ActivityB', 'ActivityC'):
    registerables.append(swf.ActivityType(domain=swf_domain, name=activity_type, version=VERSION, task_list='default'))

for swf_entity in registerables:
    try:
        swf_entity.register()
        print swf_entity.name, 'registered successfully'
    except (SWFDomainAlreadyExistsError, SWFTypeAlreadyExistsError):
        print swf_entity.__class__.__name__, swf_entity.name, 'already exists'

@app.route('/')
def api():
    starttime=time.time()
    uid=binascii.hexlify(os.urandom(10))
    logging.info(str(starttime) + " is the start time")
    command = swf.WorkflowType(name='HelloWorkflow', domain=swf_domain, version=VERSION, task_list='default',workflowId=uid).start()
    requestid=command.workflowId
    print requestid
    while r.get(requestid) is None:
        pass
    endtime=time.time()
    logging.info(str(endtime) + " is the end time")
    elapsedtime=str(endtime-starttime)
    response = r.get(requestid)
    print response
    return response + " The total backend processing time was %s seconds" %elapsedtime


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
