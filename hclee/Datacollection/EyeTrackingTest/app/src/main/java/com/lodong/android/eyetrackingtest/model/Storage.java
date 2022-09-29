package com.lodong.android.eyetrackingtest.model;

import java.io.Serializable;

//사용자의 선택값에 따른 경로 값을 담는 클래스
public class Storage implements Serializable {
    private static Storage instance;
    private String storage;

    private String lastSaveVideo;
    private String lastSaveTxt;

    private Storage(){};

    public static Storage getInstance(){
        if(instance == null){
            instance = new Storage();
        }
        return instance;
    }


    public String getStorage() {
        return storage;
    }

    public void setStorage(String storage) {
        this.storage = storage;
    }

    public static void setInstance(Storage instance) {
        Storage.instance = instance;
    }

    public String getLastSaveVideo() {
        return lastSaveVideo;
    }

    public void setLastSaveVideo(String lastSaveVideo) {
        this.lastSaveVideo = lastSaveVideo;
    }

    public String getLastSaveTxt() {
        return lastSaveTxt;
    }

    public void setLastSaveTxt(String lastSaveTxt) {
        this.lastSaveTxt = lastSaveTxt;
    }


}
