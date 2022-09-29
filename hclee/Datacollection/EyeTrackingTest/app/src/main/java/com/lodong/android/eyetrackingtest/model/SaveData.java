package com.lodong.android.eyetrackingtest.model;

@Deprecated
public class SaveData {
    private static SaveData instance;
    private String saveVideoDownloadUri;
    private String saveTxtDownloadUri;

    private SaveData(){}

    public static SaveData getInstance(){
        if(instance == null){
            instance = new SaveData();
        }

        return instance;
    }

    public String getSaveVideoDownloadUri() {
        return saveVideoDownloadUri;
    }

    public void setSaveVideoDownloadUri(String saveVideoDownloadUri) {
        this.saveVideoDownloadUri = saveVideoDownloadUri;
    }

    public String getSaveTxtDownloadUri() {
        return saveTxtDownloadUri;
    }

    public void setSaveTxtDownloadUri(String saveTxtDownloadUri) {
        this.saveTxtDownloadUri = saveTxtDownloadUri;
    }
}
