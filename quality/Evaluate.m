%% Matlab script for calculating speech enhancement metrics for multiple files
%composite.m for individual comparisons required. Available here: https://ecs.utdallas.edu/loizou/speech/composite.zip
%Metrics used: PESQ, CSIG, CBAK, COVL and SSNR

clc; clear; % clear command window and workspace

files = dir('../../clean_testset_wav_16000/p*'); % directory to reference clean and enhanced speech files

f=zeros(824,2);
for k = 1:length(files)
   file = files(k).name;
   [sig(k),bak(k),ovl(k)] = composite(['../../clean_testset_wav_16000/' file], ['../../output_sources/' file '_speech.wav']);
   f(k,1) = sig(k);
   f(k,2) = bak(k);
   f(k,3) = ovl(k);
end
