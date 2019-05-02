% PHYS2921
% William Talbot
% SSP Neural Net Analysis

clc;
clear;
close all;

% Read files
perf = csvread('csvfiles/performances.csv');
sum = csvread('csvfiles/weights_sum.csv');
mean = csvread('csvfiles/weights_mean.csv');
var = csvread('csvfiles/weights_var.csv');
init_weights = csvread('csvfiles/weights_init.csv');
final_weights = csvread('csvfiles/weights_final.csv');

figure;
subplot(2,2,1);
plot(1:length(perf),perf);
title('preformance');
subplot(2,2,2);
plot(1:length(sum),sum);
title('sum');
subplot(2,2,3);
plot(1:length(mean),mean);
title('mean');
subplot(2,2,4);
plot(1:length(var),var);
title('var');

figure;
subplot(1,2,1);
[counts, bin_loc] = hist(init_weights,sqrt(length(init_weights)));
bar(bin_loc, counts);
subplot(1,2,2);
[counts, bin_loc] = hist(final_weights,sqrt(length(final_weights)));
bar(bin_loc, counts);