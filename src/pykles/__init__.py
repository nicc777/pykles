import os
import logging
from datetime import datetime
import traceback


###############################################################################
###                                                                         ###
###                    L O G G I N G   A N D   S E T U P                    ###
###                                                                         ###
###############################################################################


debug_flag = False
try:
    debug_flag = bool(int(os.getenv('DEBUG', '0')))
except:
    pass
logger_level = logging.INFO
if debug_flag is True:
    logger_level = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(logger_level)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d -  %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logger_level)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logger_level)


###############################################################################
###                                                                         ###
###                 S U P P O R T I N G    F U N C T I O N S                ###
###                                                                         ###
###############################################################################

def get_utc_timestamp(with_decimal: bool=False): # pragma: no cover
    epoch = datetime(1970,1,1,0,0,0) 
    now = datetime.utcnow() 
    timestamp = (now - epoch).total_seconds() 
    if with_decimal: 
        return timestamp 
    return int(timestamp) 


def _extract_number(value: str)->float:
    result = 0.0
    try:
        i = ''
        for l in value:
            if l == '.' or l.isdigit():
                i = '{}{}'.format(i, l)
        result = float(i)
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    return result


def kubernetes_unit_conversion(value: str)->float:
    """
        References:
            * https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/
            * https://physics.nist.gov/cuu/Units/binary.html
    """
    result = 0
    if value.endswith('d'):
        result = value=_extract_number(value=value) / 10                    # deci
    elif value.endswith('c'):
        result = value=_extract_number(value=value) / 100                   # centi
    elif value.endswith('m'):
        result = value=_extract_number(value=value) / 1000                  # milli
    elif value.endswith('u'):
        result = value=_extract_number(value=value) / 1000000               # micro
    elif value.endswith('n'):
        result = value=_extract_number(value=value) / 1000000000            # nano
    elif value.endswith('h'):
        result = value=_extract_number(value=value) * 100
    elif value.endswith('Ki'):
        result = value=_extract_number(value=value) * 2**10                 # 2^10 for KiB
    elif value.endswith('k'):
        result = value=_extract_number(value=value) * 1000
    elif value.endswith('Mi'):
        result = value=_extract_number(value=value) * 2**20                 # 2^20 for MiB
    elif value.endswith('M'):
        result = value=_extract_number(value=value) * 1000000
    elif value.endswith('Gi'):
        result = value=_extract_number(value=value) * 2**30                 # 2^30 for Gib
    elif value.endswith('G'):
        result = value=_extract_number(value=value) * 1000000000
    elif value.endswith('Ti'):
        result = value=_extract_number(value=value) * 2**40                 # 2^40 for TiB
    elif value.endswith('T'):
        result = value=_extract_number(value=value) * 1000000000000
    elif value.endswith('Pi'):
        result = value=_extract_number(value=value) * 2**50                 # 2^50 for PiB
    elif value.endswith('P'):
        result = value=_extract_number(value=value) * 1000000000000000
    else:
        result = _extract_number(value=value)        
    return float(result)

