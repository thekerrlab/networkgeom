% PHYS2921
% William Talbot
% SSP Neural Net Analysis

clc;
clear;
close all;

%% Options
option_read_files       = true;
option_performance      = true;
option_weights_hist     = true;
option_weights_3D       = false;
option_occup_grid       = false;
option_food_gather      = true;
option_output_freqs     = true;
option_spiking_data     = true;
option_animate          = false;
animate_speed = 100; % Animation Frequency

%% Read files
if option_read_files
    fprintf('READING performances.csv...');
    perf = csvread('csvfiles/performances.csv');fprintf(' READ.\n');
    fprintf('READING exc_stdp_weights.csv...');
    exc_stdp_weights = csvread('csvfiles/exc_out_weights.csv');fprintf(' READ.\n');
    fprintf('READING inh_weights.csv...');
    inh_weights = csvread('csvfiles/inh_out_weights.csv');fprintf(' READ.\n');
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
end
%% Calculations
if option_read_files
    num_epochs = length(perf);
    fprintf('CALCULATING weight sums, averages and variance...');
    sumW = sum(exc_stdp_weights, 2);
    meanW = mean(exc_stdp_weights, 2);
    varW = var(exc_stdp_weights,0,2);
    fprintf('\tCALCULATED\n');

    init_exc_stdp_weights = exc_stdp_weights(1,:);
    final_exc_stdp_weights = exc_stdp_weights(end,:);
    init_inh_weights = inh_weights(1,:);
    final_inh_weights = inh_weights(end,:);
    fprintf('Initial Sum Weight of Excitatory STDP Connections = %.3e\n', sum(init_exc_stdp_weights));
    fprintf('Final Sum Weight of Excitatory STDP Connections = %.3e\n', sum(final_exc_stdp_weights));
    fprintf('Initial Sum Weight of Inhibitory Connections = %.3e\n', sum(init_inh_weights));
    fprintf('Final Sum Weight of Inhibitory Connections = %.3e\n', sum(final_inh_weights));
end
%% Performance and Diagnostics
if option_performance
    fprintf('RUNNING Performance and Diagnostics...');
    figure;
    subplot(2,2,1);
    plot(1:length(perf),perf);
    hold on; plot([0,length(perf)], [0.1, 0.1], 'r--');
    title('performance');
    subplot(2,2,2);
    plot(1:length(sumW),sumW);
    title('sum');
    subplot(2,2,3);
    plot(1:length(meanW),meanW);
    title('mean');
    subplot(2,2,4);
    plot(1:length(varW),varW);
    title('var');

    fprintf('\tRAN\n');
end
%% Weights histogram
if option_weights_hist
    fprintf('RUNNING Weights Histogram...');
    figure;
    histogram(init_exc_stdp_weights);
    hold on;
    histogram(final_exc_stdp_weights);
    title('Initial Excitatory STDP Weights Distribution');
    legend('Initial','Final');

    if std(inh_weights(end,:)) > 1e-10
        figure;
        histogram(init_inh_weights);
        hold on;
        histogram(final_inh_weights);
        title('Initial Inhibitory Weights Distribution');
        legend('Initial','Final');
    end

    fprintf('\tRAN\n');
end
%% Weights distribution
if option_weights_3D
    fprintf('RUNNING Weights Distribution...');
    figure;
    %h = gobjects(1,length(weights(:,1)));
    binNumber = 100;
    bins  = zeros(length(exc_stdp_weights(:,1)),binNumber);
    for i = 1:length(exc_stdp_weights(:,1))
        h = histogram(exc_stdp_weights(i,:), binNumber);
        bins(i,:) = h.Values;
    end
    bargraph = bar3(bins);
    for b = bargraph
        set(b, 'EdgeAlpha', 0);
    end
    xlabel('Bins');
    ylabel('Epochs');
    zlabel('Number');

    fprintf('\tRAN\n');
end
%% Plot the occupancy grid and the path
path = path_data + 0.5;
if option_occup_grid
    fprintf('RUNNING Occupancy Grid...');
    map = robotics.BinaryOccupancyGrid(length(final_grid(1,:)),length(final_grid),1);
    occupiedRowsCols = [];
    for row = 1:length(final_grid)
        for col = 1:length(final_grid(1,:))
            if final_grid(row, col) == 1
                occupiedRowsCols = [occupiedRowsCols;col, row];
            end
        end
    end
    % Add in collected food
    if ~isempty(collected_food)
        for row = 1:length(collected_food(:,1))
            occupiedRowsCols = [occupiedRowsCols;collected_food(row, 1), collected_food(row, 2)];
        end
    end
    setOccupancy(map, occupiedRowsCols, 1);
    % Plot the path, first adjusting for matlab's indexing, then +0.5 for
    % location in grid
    path = path_data + 0.5;
    % Find indices where we cross a grid border
    indices = [];
    for idx = 2:length(path)
        if ((path(idx,1) + path(idx-1,1) == length(final_grid)) && path(idx,1) ~= path(idx-1,1))  ...
                       || ((path(idx,2) + path(idx-1,2) == length(final_grid(1,:))) && path(idx,2) ~= path(idx-1,2))
            indices = [indices,idx];
        end
    end
    indices = [indices,length(path)+1];
    figure;
    show(map);
    set(gca, 'YDir', 'reverse');
    grid minor;
    hold on;
    plot(path(1:(indices(1)-1),1),path(1:(indices(1)-1),2), 'r', 'LineWidth', 2);
    for i = 2:length(indices)
        plot(path(indices(i-1):(indices(i)-1),1),path(indices(i-1):(indices(i)-1),2), 'r', 'LineWidth', 2);
    end

    fprintf('\tRAN\n');
end
%% Epochs of food gathering
if option_food_gather
    fprintf('RUNNING Food Gathering Analysis...');
    if ~isempty(collected_food)
        cf_index = 1;
        times = zeros(1,length(collected_food(:,1)));
        for i = 1:length(path(:,1))
            if (path(i,:)-0.5) == collected_food(cf_index,:)
                times(cf_index) = i;
                cf_index = cf_index + 1;
                if cf_index >= length(collected_food(:,1))
                    break;
                end
            end
        end
        times = times(times > 0);
    else
        times = [];
    end
    figure;
    subplot(1,2,1);
    %plot(1:length(times),times);
    histogram(times,20);
    title('Times of gathered food')
    xlabel('Epoch');
    ylabel('Number of food gathered');

    subplot(1,2,2);
    performance_100 = zeros(1,num_epochs);
    for e = 1:num_epochs
        performance_100(e) = length(times(times <= e & times > max(0,e-100)))/100;
    end
    fit_gather = polyfit(1:num_epochs,performance_100,1);
    yfit_gather = polyval(fit_gather,1:num_epochs);
    plot(1:num_epochs, performance_100);
    hold on;
    plot(1:num_epochs, yfit_gather, 'LineWidth', 2);
    title('Performance over last 100 Epochs');
    xlabel('Epoch');
    ylabel('Gathering Rate');

    fprintf('\tRAN\n');
end
%% Output cell Frequencies
if option_output_freqs
    fprintf('RUNNING Output Cell Frequency Analysis...');
    if ~isempty(output_cell_frequencies)
        figure;
        hold on;
        for cell = 1:length(output_cell_frequencies(1,:))
            plot(1:length(output_cell_frequencies(:,cell)), output_cell_frequencies(:,cell));
        end
    end
    xlabel('Epochs');
    ylabel('Frequency (Hz)');
    title('Output Cell Frequencies');

    fprintf('\tRAN\n');
end
%% Spiking data
if option_spiking_data
    fprintf('RUNNING Spiking Data Analysis...');
    epoch_spike_indices = floor(spkt/300);
    spikes_per_epoch = zeros(1,num_epochs);
    for e = 1:num_epochs
        spikes_per_epoch(e) = length(spkid(epoch_spike_indices == e & spkid > (max(spkid)-9)));
    end
    fit_spike = polyfit(1:num_epochs,spikes_per_epoch,1);
    yfit_spike = polyval(fit_spike,1:num_epochs);
    figure;
    subplot(1,2,1);
    histogram(spikes_per_epoch);
    title('Spikes/Epoch');
    xlabel('Number of Spikes');
    ylabel('Number of Epochs');
    subplot(1,2,2);
    plot(1:num_epochs, spikes_per_epoch);
    hold on;
    plot(1:num_epochs, yfit_spike, 'LineWidth', 2);
    title('Spikes/Epoch');
    xlabel('Epoch Number');
    ylabel('Number of Spikes');

    fprintf('\tRAN\n');
end
%% Animation
if option_animate
    fprintf('RUNNING Path Animation...');
    % Animation
    figure;
    show(map);
    grid on;
    set(gca, 'YDir', 'reverse');
    hold on;
    index = 1;
    for i = 2:length(path)
        if i ~= indices(index)
            plot(path(i-1:i, 1),path(i-1:i, 2), 'r', 'LineWidth', 2);
        else
            index = index + 1;
        end
        pause(1/animate_speed);
    end
    fprintf('\tRAN\n');
end