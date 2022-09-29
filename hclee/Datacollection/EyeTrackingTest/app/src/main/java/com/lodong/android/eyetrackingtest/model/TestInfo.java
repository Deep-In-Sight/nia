package com.lodong.android.eyetrackingtest.model;

import java.io.Serializable;

public class TestInfo implements Serializable {
    private static TestInfo instance;
    private final String[] postureList = {"서기", "앉기", "한손 기기 사용", "음식 섭취", "무릎 거치", "휴대폰 사용", "턱 괴기", "위로 눕기", "옆으로 눕기", "엎드리기"};
    private final String[] directionList = {"카메라 - 좌측에 위치", "카메라 - 상단에 위치", "카메라 - 우측에 위치"};
    private final String[] statusList = {"집중", "졸림", "집중 결핍(산만)", "집중 하락", "태만(이탈)"};
    private final String[][] statusCond= {
            {"상체는 움직이지 말아주세요.", "집중하며 움직이는 포인터를 응시해주세요"},
            {"상체는 움직이지 말아주세요", "눈을 자주 깜빡여주세요.", "하품을 해주세요"},
            {"상체는 움직이지 말아주세요.", "움직이는 포인터를 잘 응시해주세요."},
            {"상체는 움직이지 말아주세요.", "포인터를 잘 응시해주세요."},
            {"상체는 움직이지 말아주세요.","움직이는 포인터를 응시해주세요."}
    };

    private int scenarioNum;

    private int posture;
    private String postureString;
    private int deviceDirection;
    private String deviceDirectionString;
    private int status;
    private String statusString;

    private String testTime;

    private int lastSelectIndex=0;

    private int retry = 1;

    private TestInfo(){}

    public static TestInfo getInstance(){
        if(instance == null){
            instance = new TestInfo();
        }
        return instance;
    }

    public int getScenarioNum() {
        return scenarioNum;
    }

    public void setScenarioNum(int scenarioNum) {
        this.scenarioNum = scenarioNum;
        if(scenarioNum != 10){
            lastSelectIndex = scenarioNum;
        }
    }

    public int getPosture() {
        return posture;
    }

    public void setPosture(int posture) {
        this.posture = posture;
        setPostureString(postureList[posture]);
    }

    public String getPostureString() {
        return postureString;
    }

    public void setPostureString(String postureString) {
        this.postureString = postureString;
    }

    public int getDeviceDirection() {
        return deviceDirection;
    }

    public void setDeviceDirection(int deviceDirection) {
        this.deviceDirection = deviceDirection;
        setDeviceDirectionString(directionList[deviceDirection]);
    }

    public String getDeviceDirectionString() {
        return deviceDirectionString;
    }

    public void setDeviceDirectionString(String deviceDirectionString) {
        this.deviceDirectionString = deviceDirectionString;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
        setStatusString(statusList[status]);
        if(status == 1 || status == 3){
            setScenarioNum(10);
        }else{
            if(this.scenarioNum == 10){
                this.scenarioNum = lastSelectIndex;
            }
        }
    }

    public String getStatusString() {
        return statusString;
    }

    public void setStatusString(String statusString) {
        this.statusString = statusString;
    }

    public String[][] getStatusCond() {
        return statusCond;
    }

    public String getTestTime() {
        return testTime;
    }

    public void setTestTime(String testTime) {
        this.testTime = testTime;
    }

    public static void setInstance(TestInfo instance) {
        TestInfo.instance = instance;
    }

    public int getRetry() {
        return retry;
    }

    public void setRetry(int retry) {
        this.retry = retry;
    }

    public int getLastSelectIndex() {
        return lastSelectIndex;
    }

    public void setLastSelectIndex(int lastSelectIndex) {
        this.lastSelectIndex = lastSelectIndex;
    }
}
