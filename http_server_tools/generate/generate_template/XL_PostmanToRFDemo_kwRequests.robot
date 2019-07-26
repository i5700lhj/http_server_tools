*** Settings ***
Library           TestLibrary
Library           RequestsLibrary

*** Keywords ***
XL_DemoGet-Params
    [Arguments]    ${host}    ${data}
    [Documentation]   【功能】   这里填写接口说明，必须按此格式填写

    ...

    ...    【参数】

    ...

    ...    【返回值】

    ...
    ${headers}    Create Dictionary    Content-Type=application/x-www-form-urlencoded    Channel=0x10800001    Platform-Version=9.3.1    App-Type=android    Mobile-Type=android    Version-Name=5.17.12.4000    Version-Code=5390    Product-Id=31    IMEI=78728a99d222939    idfa=209090da78d    Peer-Id=4efb29b4b6442be50410fd499b9f20de    User-Id=55441701    Session-Id=4668844    
    Create Session    api    ${host}    ${headers}   verify=${False}
    ${Ret}    Get Request   api   /api/adp/get?${data}
    [Return]    ${Ret}

XL_DemoPost-Body-FormUrlencoded
    [Arguments]    ${host}    ${data}
    [Documentation]   【功能】   这里填写接口说明，必须按此格式填写

    ...

    ...    【参数】

    ...

    ...    【返回值】

    ...
    ${headers}    Create Dictionary    Content-Type=application/x-www-form-urlencoded    
    Create Session    api    ${host}    ${headers}   verify=${False}
    ${Ret}    Post Request   api   /api/adp/reloadApp    data=${data}
    [Return]    ${Ret}

XL_DemoPost-Body-FormRawJson
    [Arguments]    ${host}    ${data}
    [Documentation]   【功能】   这里填写接口说明，必须按此格式填写

    ...

    ...    【参数】

    ...

    ...    【返回值】

    ...
    ${headers}    Create Dictionary    Content-Type=application/json    
    Create Session    api    ${host}    ${headers}   verify=${False}
    ${Ret}    Post Request   api   /login    data=${data}
    [Return]    ${Ret}

