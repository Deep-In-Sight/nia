package com.lodong.android.eyetrackingtest.model;

import android.util.Log;

import androidx.annotation.NonNull;
import androidx.lifecycle.MutableLiveData;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

public class RealTimeDatabaseInterface {
    private final String TAG = RealTimeDatabaseInterface.class.getSimpleName();
    private FirebaseDatabase database = FirebaseDatabase.getInstance("https://eyetracker-8de2c-default-rtdb.asia-southeast1.firebasedatabase.app/");
    private final String DEVICE_TYPE_SMARTPHONE = "스마트폰";
    private final String DEVICE_TYPE_TABLET = "태블릿";
    private DatabaseReference myRef;
    private User user;
    private TestInfo testInfo;
    private String deviceType;
    private String birthAndName;
    private String third;

    private MutableLiveData<Boolean> loadingUploadVideoUrl = new MutableLiveData<>();
    private MutableLiveData<Boolean> loadingUploadTxtUrl = new MutableLiveData<>();

    public RealTimeDatabaseInterface(){
        user = User.getInstance();
        testInfo = TestInfo.getInstance();

        myRef = database.getReference();

        deviceType = user.getDevice_type();
        if (user.getDevice_type().equals(DEVICE_TYPE_SMARTPHONE)) {
            deviceType = "smartPhone";
        } else {
            deviceType = "tablet";
        }
        birthAndName = user.getBirth() + "_" + user.getName();
        third = testInfo.getScenarioNum() + "_"
                +testInfo.getPostureString() + "_"
                +testInfo.getDeviceDirectionString() + "_"
                +testInfo.getStatusString();

    }

    public void sendVideoUrl(String downloadLink){
        Log.d(TAG, "sendVideoUrl");
        myRef.child("eyetracking").child(deviceType).child(birthAndName).child(TestInfo.getInstance().getTestTime()).child(third).child("video").setValue(downloadLink)
                .addOnCompleteListener(task -> {
                    if(task.isSuccessful()){
                        Log.d(TAG, "send video link success");
                    }else{
                        Log.d(TAG, "send video link failed");

                    }
                });
    }

    public void sendGyroValueUrl(String downloadLink){
        Log.d(TAG, "sendGyroValueUrl");
        myRef.child("eyetracking").child(deviceType).child(birthAndName).child(TestInfo.getInstance().getTestTime()).child(third).child("gyro").setValue(downloadLink)
                .addOnCompleteListener(task -> {
                    if(task.isSuccessful()){
                        Log.d(TAG, "send gyro link success");
                    }else{
                        Log.d(TAG, "send gyro link failed");

                    }
                });
    }

    public MutableLiveData<Boolean> getLoadingUploadVideoUrl() {
        return loadingUploadVideoUrl;
    }

    public MutableLiveData<Boolean> getLoadingUploadTxtUrl() {
        return loadingUploadTxtUrl;
    }
}
