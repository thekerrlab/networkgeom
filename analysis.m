% PHYS2921
% William Talbot
% SSP Neural Net Analysis

clc;
close all;

%% Variables From Sim
%epoch_time = 300; % ms
%middle_pop_size = 28^2;

%% Options %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
option_load_mat_file    = true;
mat_file = 'matfiles/epoch_1000_test.mat';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
option_performance      = true;
option_weights_hist     = true;
option_weights_3D       = false;
option_occup_grid       = true;
option_food_gather      = true;
option_output_freqs     = true;
option_spiking_data     = true;
option_weights_heatmap  = true;
option_animate          = false;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
add_collected_food = true;
animate_speed = 100; % Animation Frequency
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Read files
if option_load_mat_file
    fprintf('LOADING %s...', mat_file);
    load(mat_file);
    fprintf('\tLOADED\n');
    num_epochs = length(perf);
    fprintf('CALCULATING weight sums, averages and variance...');
    sumW = sum(exc_out_weights, 2);
    meanW = mean(exc_out_weights, 2);
    varW = var(exc_out_weights,0,2);
    fprintf('\tCALCULATED\n');
    
    fprintf('CONVERTING path to matlab indexing and to double...');
    path = double(path) + 1;
    fprintf('\tCONVERTED\n');
    fprintf('CONVERTING collected_food to matlab indexing and to double...');
    collected_food = double(collected_food) + 1;
    fprintf('\tCONVERTED\n');
    epoch_time = double(epoch_time);
    middle_pop_size = double(middle_pop_size);
    init_exc_out_weights = exc_out_weights(1,:);
    final_exc_out_weights = exc_out_weights(end,:);
    init_inh_out_weights = inh_out_weights(1,:);
    final_inh_out_weights = inh_out_weights(end,:);
end
%% Prints
fprintf('Initial Sum Weight of Excitatory STDP Connections = %.3e\n', sum(init_exc_out_weights));
fprintf('Final Sum Weight of Excitatory STDP Connections = %.3e\n', sum(final_exc_out_weights));
fprintf('Initial Sum Weight of Inhibitory Connections = %.3e\n', sum(init_inh_out_weights));
fprintf('Final Sum Weight of Inhibitory Connections = %.3e\n', sum(final_inh_out_weights));

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
    histogram(init_exc_out_weights);
    hold on;
    histogram(final_exc_out_weights);
    title('Initial Excitatory STDP Weights Distribution');
    legend('Initial','Final');

    if std(inh_out_weights(end,:)) > 1e-10
        figure;
        histogram(init_inh_out_weights);
        hold on;
        histogram(final_inh_out_weights);
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
    bins  = zeros(length(exc_out_weights(:,1)),binNumber);
    for i = 1:length(exc_out_weights(:,1))
        h = histogram(exc_out_weights(i,:), binNumber);
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
path_data = path - 0.5;
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
    if ~isempty(collected_food) && add_collected_food
        for row = 1:length(collected_food(:,1))
            occupiedRowsCols = [occupiedRowsCols;collected_food(row, 1), collected_food(row, 2)];
        end
    end
    setOccupancy(map, occupiedRowsCols, 1);
    % Plot the path, first adjusting for matlab's indexing, then +0.5 for
    % location in grid
    %path_data = path_data + 0.5;
    % Find indices where we cross a grid border
    indices = [];
    for idx = 2:length(path)
        if ((path_data(idx,1) + path_data(idx-1,1) == length(final_grid)) && path_data(idx,1) ~= path_data(idx-1,1))  ...
                       || ((path_data(idx,2) + path_data(idx-1,2) == length(final_grid(1,:))) && path_data(idx,2) ~= path_data(idx-1,2))
            indices = [indices,idx];
        end
    end
    indices = [indices,length(path)+1];
    figure;
    show(map);
    set(gca, 'YDir', 'reverse');
    grid minor;
    hold on;
    plot(path_data(1:(indices(1)-1),1),path_data(1:(indices(1)-1),2), 'r', 'LineWidth', 2);
    for i = 2:length(indices)
        plot(path_data(indices(i-1):(indices(i)-1),1),path_data(indices(i-1):(indices(i)-1),2), 'r', 'LineWidth', 2);
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
            if (path(i,:)) == collected_food(cf_index,:)
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
    epoch_spike_indices = floor(spkt/epoch_time);
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
%% Synaptic weights heatmap before and after
if option_weights_heatmap
    fprintf('RUNNING Synaptic Weight Heatmap...');
    grid_len = sqrt(middle_pop_size);
    figure('Position', [0,0,1500,1000]);
    heatmap_weights_grid = zeros(grid_len,grid_len);
    for output_cell_num = 1:9
        subplot(3,3,output_cell_num);
        for row = 1:grid_len
            heatmap_weights_grid(row,:) = init_exc_out_weights((1+(row-1)*grid_len):row*grid_len);
        end
        heatmap(heatmap_weights_grid, 'Colormap', parula);
        title(sprintf('Initial O%d', output_cell_num));
    end
    figure('Position', [0,0,1500,1000]);
    for output_cell_num = 1:9
        subplot(3,3,output_cell_num);
        for row = 1:grid_len
            heatmap_weights_grid(row,:) = final_exc_out_weights((1+(row-1)*grid_len):row*grid_len);
        end
        heatmap(heatmap_weights_grid, 'Colormap', parula);
        title(sprintf('Final O%d', output_cell_num));
    end
    fprintf('\tRAN\n');
end

%% Animation
if option_animate && option_occup_grid
    fprintf('RUNNING Path Animation...');
    % Animation
    figure;
    show(map);
    grid minor;
    set(gca, 'YDir', 'reverse');
    hold on;
    index = 1;
    for i = 2:length(path_data)
        if i ~= indices(index)
            plot(path_data(i-1:i, 1),path_data(i-1:i, 2), 'r', 'LineWidth', 2);
        else
            index = index + 1;
        end
        pause(1/animate_speed);
    end
    fprintf('\tRAN\n');
end