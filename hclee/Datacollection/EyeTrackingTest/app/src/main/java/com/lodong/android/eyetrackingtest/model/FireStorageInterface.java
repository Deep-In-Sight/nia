package com.lodong.android.eyetrackingtest.model;


import android.net.Uri;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.lifecycle.MutableLiveData;

import com.google.android.gms.tasks.Continuation;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;
import com.google.firebase.storage.UploadTask;
import com.lodong.android.eyetrackingtest.ResultActivity;

import java.io.InputStream;

public class FireStorageInterface {
    private final String TAG = FireStorageInterface.class.getSimpleName();
    private FirebaseStorage storage;
    private StorageReference storageRef;

    private final String DEVICE_TYPE_SMARTPHONE = "스마트폰";
    private final String DEVICE_TYPE_TABLET = "태블릿";
    private final String ROOT_FOLDER = "mobile_upload";

    private String dirDeviceType="";
    private String dirUserInfo="";
    private String dirTestInfo="";

    private MutableLiveData<Boolean> loadingUploadVideo = new MutableLiveData<>();
    private MutableLiveData<Boolean> loadingUploadTxt = new MutableLiveData<>();

    public FireStorageInterface() {
        storage = FirebaseStorage.getInstance();
        storageRef = FirebaseStorage.getInstance().getReference().child(ROOT_FOLDER);
        Log.d(TAG, "1 : "+storageRef.getPath());
    }

    public void settingDirectory() {
        User user = User.getInstance();
        TestInfo testInfo = TestInfo.getInstance();

        if (user.getDevice_type().equals(DEVICE_TYPE_SMARTPHONE)) {
            dirDeviceType = "smartPhone";
        } else {
            dirDeviceType = "tablet";
        }

        String direcUser = user.getBirth() + "_" + user.getName();
        dirUserInfo = direcUser;

        String direcTest = testInfo.getScenarioNum() + "_"
                + testInfo.getPostureString().replace(" ", "") + "_"
                + testInfo.getDeviceDirectionString().replace(" ", "") + "_"
                + testInfo.getStatusString().replace(" ", "");

        dirTestInfo = direcTest;
    }

    public void upload(InputStream videoStream,InputStream txtStream, ResultActivity.UploadListener listener){
        uploadVideo(videoStream, txtStream, listener);
    }

    public void uploadVideo(InputStream videoStream, InputStream txtStream, ResultActivity.UploadListener listener) {
        loadingUploadVideo.setValue(true);
        storageRef = FirebaseStorage.getInstance().getReference().child(ROOT_FOLDER).child(dirDeviceType).child(dirUserInfo).child(TestInfo.getInstance().getTestTime()).child(dirTestInfo).child("video.mp4");
        Log.d(TAG, "4: " + storageRef.getPath());
        UploadTask uploadTask = storageRef.putStream(videoStream);
        uploadTask.continueWithTask(task -> {
            if(!task.isSuccessful()){
                throw task.getException();
            }
            storageRef.getDownloadUrl().addOnSuccessListener(new OnSuccessListener<Uri>() {
                @Override
                public void onSuccess(Uri uri) {
                    Log.d(TAG, uri.toString());
                    SaveData save = SaveData.getInstance();
                    save.setSaveVideoDownloadUri(uri.toString());
                    uploadGyroValue(txtStream, listener);
                    loadingUploadVideo.setValue(false);

                }
            });
            return storageRef.getDownloadUrl();
        }).addOnFailureListener(e -> {
            e.printStackTrace();
            loadingUploadVideo.setValue(false);
            listener.onFailed(e);
        }).addOnSuccessListener(taskSnapshot -> {
            listener.onSuccess();
        });
    }

    public void uploadGyroValue(InputStream inputStream, ResultActivity.UploadListener listener) {
        loadingUploadTxt.setValue(true);
        storageRef = FirebaseStorage.getInstance().getReference().child(ROOT_FOLDER).child(dirDeviceType).child(dirUserInfo).child(TestInfo.getInstance().getTestTime()).child(dirTestInfo).child("gyro.txt");
        UploadTask uploadTask = storageRef.putStream(inputStream);
        uploadTask.continueWithTask(task -> {
            if(!task.isSuccessful()){
                throw task.getException();
            }
            storageRef.getDownloadUrl().addOnSuccessListener(new OnSuccessListener<Uri>() {
                @Override
                public void onSuccess(Uri uri) {
                    Log.d(TAG, uri.toString());
                    SaveData save = SaveData.getInstance();
                    save.setSaveTxtDownloadUri(uri.toString());
                    loadingUploadTxt.setValue(false);

                }
            });
            return storageRef.getDownloadUrl();
        }).addOnFailureListener(e -> {
            e.printStackTrace();
            loadingUploadTxt.setValue(false);
            listener.onFailed(e);
        }).addOnSuccessListener(taskSnapshot -> {
            listener.onSuccess();
        });
    }

    public MutableLiveData<Boolean> getLoadingUploadVideo() {
        return loadingUploadVideo;
    }

    public MutableLiveData<Boolean> getLoadingUploadTxt() {
        return loadingUploadTxt;
    }
}
