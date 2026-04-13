import sys
import os
module=sys.argv[1];
f1 = open("pkgSrc",'r')
for i in f1 :
    if module in i :
        t=i.split(":");
        file=t[0];
        b=os.path.basename(file);
        # ends with .py 
        imp_file =b[0:-3]
        defin = t[1];
        d2=defin[6:]
        idx=d2.find("(")
        if ( idx != -1 ) :
            d2=d2[0:idx]
        print("from ."+imp_file+" import ", d2);
