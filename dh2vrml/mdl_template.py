
TEMPLATE = """Model {{
  Name			  "{NAME}"
  Version		  6.4
  SavedCharacterEncoding  "UTF-8"
  ModelUUID		  "be2d90c9-ff0f-411f-9ac3-fcc789d53354"
  GraphicalInterface {{
    NumRootInports	    0
    NumRootOutports	    0
    ParameterArgumentNames  ""
    ComputedModelVersion    "1.1"
    NumModelReferences	    0
    NumTestPointedSignals   0
    NumProvidedFunctions    0
    NumRequiredFunctions    0
    NumResetEvents	    0
    HasInitializeEvent	    0
    HasTerminateEvent	    0
    PreCompExecutionDomainType "Unset"
    IsExportFunctionModel   0
    IsArchitectureModel	    0
    IsAUTOSARArchitectureModel 0
    NumParameterArguments   0
    NumExternalFileReferences 1
    ExternalFileReference {{
      Reference		      "vrlib/VR Sink"
      Path		      "{NAME}/VR Sink"
      SID		      "1"
      Type		      "LIBRARY_BLOCK"
    }}
    OrderedModelArguments   1
  }}
  System {{
    Name		    "{NAME}"
    Location		    [29, 52, 1337, 739]
    SystemRect		    [0.000000, 0.000000, 0.000000, 0.000000]
    Open		    on
    PortBlocksUseCompactNotation off
    SetExecutionDomain	    off
    ExecutionDomainType	    "Deduce"
    ModelBrowserVisibility  on
    ModelBrowserWidth	    200
    ScreenColor		    "white"
    PaperOrientation	    "landscape"
    PaperPositionMode	    "auto"
    PaperType		    "usletter"
    PaperUnits		    "inches"
    TiledPaperMargins	    [0.500000, 0.500000, 0.500000, 0.500000]
    TiledPageScale	    1
    ShowPageBoundaries	    off
    ZoomFactor		    "100"
    ReportName		    "simulink-default.rpt"
    SIDHighWatermark	    "6"
    SimulinkSubDomain	    "Simulink"
    Block {{
      BlockType		      Constant
      Name		      "Constant"
      SID		      "2"
      Position		      [455, 140, 495, 170]
      ZOrder		      2
      Value		      "[0 0 1]"
    }}
    Block {{
      BlockType		      Mux
      Name		      "Mux"
      SID		      "6"
      Ports		      [2, 1]
      Position		      [540, 146, 545, 184]
      ZOrder		      306
      Inputs		      "2"
      DisplayOption	      "bar"
    }}
    Block {{
      BlockType		      Reference
      Name		      "VR Sink"
      SID		      "1"
      Ports		      [2]
      Position		      [460, 202, 545, 253]
      ZOrder		      1
      LibraryVersion	      "3.0"
      SourceBlock	      "vrlib/VR Sink"
      SourceType	      "Virtual Reality Sink"
      SourceProductBaseCode   "SL"
      InstantiateOnLoad	      on
      MultiThreadCoSim	      "auto"
      SampleTime	      "0.1"
      ViewEnable	      on
      RemoteChange	      off
      RemoteView	      off
      FieldsWritten	      "{FIELDS}"
      WorldFileName	      "{X3DPATH}"
      AutoView		      off
      VideoDimensions	      "[]"
      AllowVariableSize	      off
    }}
    Line {{
      ZOrder		      2
      SrcBlock		      "Constant"
      SrcPort		      1
      DstBlock		      "Mux"
      DstPort		      1
    }}
  }}
}}
"""
