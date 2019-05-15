% PHYS2921
% William Talbot
% SSP Neural Net File Reading

clc;
clear;
close all;

%% Change this:
filename = 'matfiles/epoch_80000.mat';

%% Read Data
fprintf('READING performances.csv...');
perf = csvread('csvfiles/performances.csv');fprintf(' READ.\n');
fprintf('READING exc_out_weights.csv...');
exc_out_weights = csvread('csvfiles/exc_out_weights.csv');fprintf(' READ.\n');
fprintf('READING inh_out_weights.csv...');
inh_out_weights = csvread('csvfiles/inh_out_weights.csv');fprintf(' READ.\n');
fprintf('READING path.csv...');
path_data = csvread('csvfiles/path.csv');fprintf(' READ.\n');
try
    fprintf('READING collected_food.csv...');
    collected_food = csvread('csvfiles/collected_food.csv');fprintf(' READ.\n');
catch
    collected_food = [];
end
fprintf('READING final_grid.csv...');
final_grid = csvread('csvfiles/final_grid.csv');fprintf(' READ.\n');
try
    fprintf('READING output_cell_frequencies.csv...');
    output_cell_frequencies = csvread('csvfiles/output_cell_frequencies.csv');fprintf(' READ.\n');
catch
    output_cell_frequencies = [];
end
fprintf('READING spkid.csv...');
spkid = csvread('csvfiles/spkid.csv');fprintf(' READ.\n');
spkid = spkid';
fprintf('READING spkt.csv...');
spkt = csvread('csvfiles/spkt.csv');fprintf(' READ.\n');
spkt = spkt';

num_epochs = length(perf);
fprintf('CALCULATING weight sums, averages and variance...');
sumW = sum(exc_out_weights, 2);
meanW = mean(exc_out_weights, 2);
varW = var(exc_out_weights,0,2);
fprintf('\tCALCULATED\n');

init_exc_out_weights = exc_out_weights(1,:);
final_exc_out_weights = exc_out_weights(end,:);
init_inh_out_weights = inh_out_weights(1,:);
final_inh_out_weights = inh_out_weights(end,:);

%% Save the file
save(filename);