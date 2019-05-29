% PHYS2921
% William Talbot
% SSP Neural Net Analysis

clc;
close all;

%% Options %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
option_load_mat_file    = true;
mat_file = 'matfiles/last_ditch_30000_1.mat';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
option_performance      = true;
option_weights_hist     = true;
option_weights_3D       = true;
option_occup_grid       = false;
option_food_gather      = true;
option_output_freqs     = true;
option_spiking_data     = true;
option_weights_heatmap  = true;
option_animate          = false;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
add_collected_food = true;
animate_speed = 100; % Animation Frequency
make_video = false;
video_name = 'videos/random_movement.avi';
video_quality = 25;
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
    fprintf('CONVERTING collected_food abd add_food to matlab indexing and to double...');
    collected_food = double(collected_food) + 1;
    added_food = double(added_food) + 1;
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
    hold on; plot([0,length(perf)], [0.05, 0.05], 'r--');
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
    title('Excitatory STDP Weights Distribution');
    legend('Initial','Final');

    if std(inh_out_weights(end,:)) > 1e-10
        figure;
        histogram(init_inh_out_weights);
        hold on;
        histogram(final_inh_out_weights);
        title('Inhibitory Weights Distribution');
        legend('Initial','Final');
    end

    fprintf('\tRAN\n');
end
%% Weights distribution
if option_weights_3D
    fprintf('RUNNING Weights Distribution...');
    figure;
    hold on;
    binNumber = length(exc_out_weights(:,1));
    bins  = zeros(length(exc_out_weights(:,1)),binNumber);
    for i = 1:binNumber
        h = histogram(exc_out_weights(i,:), binNumber);
        %plot3(1:binNumber, ones(1,binNumber)*double(weight_indices(i)), h.Values);
        bins(i,:) = h.Values;
    end
    bargraph = bar3(double(weight_indices),bins);
    for b = bargraph
        set(b, 'EdgeAlpha', 0);
    end
    view([135,45]);
    axis([0,binNumber,0,500e3,0,100]);
    xlabel('Weight Distribution (arb u)');
    ylabel('Epochs');
    zlabel('Number');
    title('Distribution of Synapse Weights Over Time');

    fprintf('\tRAN\n');
end
%% Epochs of food gathering
if option_food_gather
    fprintf('RUNNING Food Gathering Analysis...');
%     if ~isempty(collected_food)
%         cf_index = 1;
%         times = zeros(1,length(collected_food(:,1)));
%         for i = 1:length(path(:,1))
%             if (path(i,:)) == collected_food(cf_index,:)
%                 times(cf_index) = i;
%                 cf_index = cf_index + 1;
%                 if cf_index >= length(collected_food(:,1))
%                     break;
%                 end
%             end
%         end
%         times = times(times > 0);
%     else
%         times = [];
%     end
    figure('Position',[0,0,1800,600]);
% %     subplot(1,3,1);
%     subplot(1,2,1);
%     histogram(times,20);
%     title('Times of gathered food')
%     xlabel('Epoch');
%     ylabel('Number of food gathered');

%     subplot(1,3,2);
%     performance_1000 = zeros(1,num_epochs);
%     for e = 1:num_epochs
%         performance_1000(e) = length(times(times <= e & times > max(0,e-1000)))/1000;
%     end
%     fit_gather = polyfit(1:num_epochs,performance_1000,1);
%     yfit_gather = polyval(fit_gather,1:num_epochs);
%     plot(1:num_epochs, performance_1000);
%     hold on;
%     plot(1:num_epochs, yfit_gather, 'LineWidth', 2);
%     plot(1:num_epochs, movmean(performance_1000,1000), 'LineWidth', 2);
%     title('Performance averaged over 1000 Epochs');
%     xlabel('Epoch');
%     ylabel('Gathering Rate');
%     legend('raw', 'last 100', 'moving average');
    
%     subplot(1,3,3);
%     subplot(1,2,2);
    timespan = floor(num_epochs/10);
    performance_timespan = zeros(1,num_epochs);
    for e = 1:num_epochs
        performance_timespan(e) = length(times(times <= e & times > max(0,e-timespan)))/timespan;
    end
    epoch_to_start_fit = floor(num_epochs/10);
    fit_gather = polyfit(epoch_to_start_fit:num_epochs,performance_timespan(epoch_to_start_fit:end),1);
    yfit_gather = polyval(fit_gather,epoch_to_start_fit:num_epochs);
    plot(1:num_epochs, performance_timespan, [0,length(perf)], [0.05, 0.05], 'r--');
    hold on;
    plot(epoch_to_start_fit:num_epochs, yfit_gather, 'LineWidth', 2);
    plot(1:num_epochs, movmean(performance_timespan,timespan), 'LineWidth', 2);
    title(sprintf('Performance averaged over %d Epochs', timespan));
    xlabel('Epoch');
    ylabel('Gathering Rate');
    legend('raw', 'chance', sprintf('last %d', timespan), 'moving average', 'location', 'southeast');

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
    % Filter for output spikes
    first_out_cell_index = (49+middle_pop_size);
    spk_output_indices = spkid >= first_out_cell_index;
    spkt_out = spkt(spk_output_indices);
    epoch_spike_indices = floor(spkt_out/epoch_time);
    spikes_per_epoch = zeros(1,num_epochs);
    for spike_epoch = epoch_spike_indices
        spikes_per_epoch(spike_epoch) = spikes_per_epoch(spike_epoch) + 1;
    end
    fit_spike = polyfit(1:num_epochs,spikes_per_epoch,1);
    yfit_spike = polyval(fit_spike,1:num_epochs);
    figure;
%     subplot(1,2,1);
    histogram(spikes_per_epoch);
    title('Spikes/Epoch');
    xlabel('Number of Spikes');
    ylabel('Number of Epochs');
%     subplot(1,2,2);
%     plot(1:num_epochs, spikes_per_epoch);
%     hold on;
%     plot(1:num_epochs, yfit_spike, 'LineWidth', 2);
%     title('Spikes/Epoch');
%     xlabel('Epoch Number');
%     ylabel('Number of Spikes');

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
            heatmap_weights_grid(row,:) = init_exc_out_weights((1+(row-1)*grid_len + (output_cell_num-1)*middle_pop_size):(row*grid_len + (output_cell_num-1)*middle_pop_size));
        end
        heatmap(heatmap_weights_grid, 'Colormap', parula);
        title(sprintf('Initial O%d', output_cell_num));
    end
    figure('Position', [0,0,1500,1000]);
    for output_cell_num = 1:9
        subplot(3,3,output_cell_num);
        for row = 1:grid_len
            heatmap_weights_grid(row,:) = final_exc_out_weights((1+(row-1)*grid_len + (output_cell_num-1)*middle_pop_size):(row*grid_len + (output_cell_num-1)*middle_pop_size));
        end
        heatmap(heatmap_weights_grid, 'Colormap', parula);
        title(sprintf('Final O%d', output_cell_num));
    end
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
%% Animation
if option_animate && option_occup_grid
    fprintf('RUNNING Path Animation...');
    pause(1);
    % Set up movie writer
    if make_video
        vidObj = VideoWriter(video_name);
        vidObj.Quality = video_quality;
        open(vidObj);
    end
    
    % Animation
    figure;
    animate_map = robotics.BinaryOccupancyGrid(length(initial_grid(1,:)),length(initial_grid),1);
    occupiedRowsCols = [];
    for row = 1:length(initial_grid)
        for col = 1:length(initial_grid(1,:))
            if initial_grid(row, col) == 1
                occupiedRowsCols = [occupiedRowsCols;col, row];
            end
        end
    end
    setOccupancy(animate_map, occupiedRowsCols, 1);
    SHOWMAP = show(animate_map);
    grid minor;
    set(gca, 'YDir', 'reverse');
    hold on;
    index = 1;
    collection_index = 1;
    for i = 2:length(path_data)
        pause(1/animate_speed);
        if collection_index <= length(collected_food)
            if path(i, 1) == collected_food(collection_index, 1) && path(i, 2) == collected_food(collection_index, 2)
                % Remove the occupancy grid object
                delete(SHOWMAP);
                % Clear collected food
                setOccupancy(animate_map, collected_food(collection_index,:), 0);
                % Add added food
                setOccupancy(animate_map, added_food(collection_index,:), 1);
                % Refresh map
                SHOWMAP = show(animate_map);
                set(gca, 'YDir', 'reverse');
                grid minor;
                uistack(SHOWMAP, 'bottom');
                
                % Replot all lines since can't figure out a way to reshow
                % without overwriting plots in matlab 2017
                %tmp_index = 1;
                %for j = 2:i
                %    if j ~= indices(tmp_index)
                %        plot(path_data(j-1:j, 1),path_data(j-1:j, 2), 'r', 'LineWidth', 2);
                %    else
                %        tmp_index = tmp_index + 1;
                %    end
                %end
                
                % Show markers
                %plot(collected_food(1:collection_index,1)-0.5,collected_food(1:collection_index,2)-0.5, 'b*');
                plot(path_data(i,1),path_data(i,2), 'b*');
                
                % increment collection_index
                collection_index = collection_index + 1;
            end
        end
        if i ~= indices(index)
            plot(path_data(i-1:i, 1),path_data(i-1:i, 2), 'r', 'LineWidth', 2);
        else
            index = index + 1;
        end
        if make_video
            writeVideo(vidObj,getframe(gcf));
        end
    end
    
    if make_video
        close(vidObj);
    end
    fprintf('\tRAN\n');
end