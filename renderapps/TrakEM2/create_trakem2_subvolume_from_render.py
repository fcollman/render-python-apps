#!/usr/bin/env python
import os
import sys
#sys.path.insert(0,'/data/array_tomography/ImageProcessing/render-python/')
#sys.path.insert(0,'/nas3/data/M270907_Scnn1aTg2Tdt_13/scripts_ff/')
import renderapi
import logging
from renderapi.utils import stripLogger
import argparse
from renderapps.TrakEM2.trakem2utils import createchunks,createheader,createproject,createlayerset,createfooters,createlayer_fromtilespecs,Chunk
import json
from renderapps.module.render_module import RenderModule, RenderParameters, TEM2ProjectTransfer
import json_module
import marshmallow as mm
import numpy as np



example_parameters = {
    "render":{
        "host":"ibs-forrestc-ux1",
        "port":8080,
        "owner":"Forrest",
        "project":"M247514_Rorb_1",
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts"
    },
    'minX':59945,
    'maxX':83341,
    'minY':84722,
    'maxY':138658,
    'minZ':24,
    'maxZ':24,
    'inputStack':'EM_fix',
    'outputStack':'EM_Site4_stitched',
    "doChunk":False,
    "outputXMLdir":"/nas3/data/M247514_Rorb_1/processed/Site4StitchFix/",
    "renderHome":"/pipeline/forrestrender/"
}

class CreateTrakEM2Project(RenderModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = TEM2ProjectTransfer
        super(CreateTrakEM2Project,self).__init__(schema_type=schema_type,*args,**kwargs)
    def run(self):
        print self.args
        self.logger.error('WARNING NEEDS TO BE TESTED, TALK TO FORREST IF BROKEN')

        zvalues = self.render.run(renderapi.stack.get_z_values_for_stack,self.args['inputStack'])

        minZ = self.args.get('minZ',int(np.min(zvalues)))
        maxZ = self.args.get('maxZ',int(np.max(zvalues)))

        if self.args['doChunk']:
            allchunks = createchunks(minZ,maxZ,self.args['chunkSize'])
        else:
            allchunks=[]
            ck = Chunk()
            ck.first = minZ
            ck.last = maxZ
            ck.dir = str(ck.first)+ "-" + str(ck.last)
            allchunks.append(ck)

        layersetfile = "layerset.xml"
        headerfile = "header.xml"

        for x in allchunks:

            outdir = os.path.join(self.args['outputXMLdir'],x.dir)
            outfile=os.path.join(outdir,'project.xml')
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            #copy header
            createheader(headerfile,outfile)
            #create project
            createproject(outfile)
            #create layerset
            createlayerset(outfile,width=(self.args['maxX']-self.args['minX']),height=(self.args['maxY']-self.args['minY']))
            #add layers
            
            for layerid in range(x.first, x.last+1):
                print "This is layerid:"        
                print layerid
                tilespecs = renderapi.tilespec.get_tile_specs_from_minmax_box(
                        self.args['inputStack'],
                        layerid,
                        self.args['minX'],
                        self.args['maxX'],
                        self.args['minY'],
                        self.args['maxY'],
                        render=self.render)
                print "Now adding layer: %d \n %d tiles"%(layerid,len(tilespecs))
                createlayer_fromtilespecs(tilespecs, outfile,layerid,shiftx=-self.args['minX'],shifty=-self.args['minY'])
                    
            #footers
            print outfile
            createfooters(outfile)

if __name__ == "__main__":
    mod = CreateTrakEM2Project(input_data= example_parameters)
    mod.run()