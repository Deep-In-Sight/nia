package com.lodong.android.eyetrackingtest.camera;

@Deprecated
public class RecordInfo {
    private final String TAG = RecordInfo.class.getSimpleName();
    private static RecordInfo instance;
    private String recordName;

    private RecordInfo(){}

    public RecordInfo getInstance(){
        if(instance == null){
            instance = new RecordInfo();
        }

        return instance;
    }

    public String getRecordName() {
        return recordName;
    }

    public void setRecordName(String recordName) {
        this.recordName = recordName;
    }
}
