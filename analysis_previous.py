# PHYS2921
# William Talbot
# SSP Neural Net Analysis

from pylab import *

## Options
option_read_files       = true;
option_performance      = true;
option_weights_hist     = true;
option_weights_3D       = false;
option_occup_grid       = false;
option_food_gather      = true;
option_output_freqs     = true;
option_spiking_data     = true;
option_animate          = false;
animate_speed = 100; # Animation Frequency

## Read files
if option_read_files:
    print('READING performances.csv...');
    perf = csvread('csvfiles/performances.csv');print(' READ.\n');
    print('READING exc_stdp_weights.csv...');
    exc_stdp_weights = csvread('csvfiles/exc_out_weights.csv');print(' READ.\n');
    print('READING inh_weights.csv...');
    inh_weights = csvread('csvfiles/inh_out_weights.csv');print(' READ.\n');
    print('READING path.csv...');
    path_data = csvread('csvfiles/path.csv');print(' READ.\n');
    try:
        print('READING collected_food.csv...');
        collected_food = csvread('csvfiles/collected_food.csv');print(' READ.\n');
    except:
        collected_food = [];

    print('READING final_grid.csv...');
    final_grid = csvread('csvfiles/final_grid.csv');print(' READ.\n');
    try:
        print('READING output_cell_frequencies.csv...');
        output_cell_frequencies = csvread('csvfiles/output_cell_frequencies.csv');print(' READ.\n');
    except:
        output_cell_frequencies = [];

    print('READING spkid.csv...');
    spkid = csvread('csvfiles/spkid.csv');print(' READ.\n');
    spkid = transpose(spkid);
    print('READING spkt.csv...');
    spkt = csvread('csvfiles/spkt.csv');print(' READ.\n');
    spkt = transpose(spkt);

## Calculations
if option_read_files:
    num_epochs = len(perf);
    print('CALCULATING weight sums, averages and variance...');
    sumW = sum(exc_stdp_weights, 2);
    meanW = mean(exc_stdp_weights, 2);
    varW = var(exc_stdp_weights,0,2);
    print('\tCALCULATED\n');

    init_exc_stdp_weights = exc_stdp_weights[0,:];
    final_exc_stdp_weights = exc_stdp_weights[-1,:];
    init_inh_weights = inh_weights[0,:];
    final_inh_weights = inh_weights[-1,:];
    print('Initial Sum Weight of Excitatory STDP Connections = %.3e\n'% sum(init_exc_stdp_weights));
    print('Final Sum Weight of Excitatory STDP Connections = %.3e\n'% sum(final_exc_stdp_weights));
    print('Initial Sum Weight of Inhibitory Connections = %.3e\n'% sum(init_inh_weights));
    print('Final Sum Weight of Inhibitory Connections = %.3e\n'% sum(final_inh_weights));

## Performance and Diagnostics
if option_performance:
    print('RUNNING Performance and Diagnostics...');
    figure();
    subplot(2,2,1);
    plot(r_[0:len(perf)],perf);
    plot([0,len(perf)], [0.1, 0.1], 'r--');
    title('performance');
    subplot(2,2,2);
    plot(r_[0:len(sumW)],sumW);
    title('sum');
    subplot(2,2,3);
    plot(r_[0:len(meanW)],meanW);
    title('mean');
    subplot(2,2,4);
    plot(r_[0:len(varW)],varW);
    title('var');

    print('\tRAN\n');

## Weights histogram
if option_weights_hist:
    print('RUNNING Weights Histogram...');
    figure();
    histogram(init_exc_stdp_weights);
#    hold on;
    histogram(final_exc_stdp_weights);
    title('Initial Excitatory STDP Weights Distribution');
    legend('Initial','Final');

    if std(inh_weights[end,:]) > 1e-10:
        figure();
        histogram(init_inh_weights);
#        hold on;
        histogram(final_inh_weights);
        title('Initial Inhibitory Weights Distribution');
        legend('Initial','Final');


    print('\tRAN\n');

## Weights distribution
if option_weights_3D:
    print('RUNNING Weights Distribution...');
    figure();
    #h = gobjects(1,len(weights(:,1)));
    binNumber = 100;
    bins  = zeros(len(exc_stdp_weights[:,0]),binNumber);
    for i in r_[0:len(exc_stdp_weights[:,0])]:
        h = histogram(exc_stdp_weights[i,:], binNumber);
        bins[i,:] = h.Values;

    bargraph = bar3(bins);
    for b in bargraph:
        set(b, 'EdgeAlpha', 0);
#    end
    xlabel('Bins');
    ylabel('Epochs');
    zlabel('Number');

    print('\tRAN\n');
#end
## Plot the occupancy grid and the path
path = path_data + 0.5;
if option_occup_grid:
    print('RUNNING Occupancy Grid...');
    map = robotics.BinaryOccupancyGrid(len(final_grid(1,:)),len(final_grid),1);
    occupiedRowsCols = [];
    for row = 1:len(final_grid)
        for col = 1:len(final_grid(1,:))
            if final_grid(row, col) == 1
                occupiedRowsCols = [occupiedRowsCols;col, row];
#            end
#        end
#    end
    # Add in collected food
    if ~isempty(collected_food)
        for row = 1:len(collected_food(:,1))
            occupiedRowsCols = [occupiedRowsCols;collected_food(row, 1), collected_food(row, 2)];
#        end
#    end
    setOccupancy(map, occupiedRowsCols, 1);
    # Plot the path, first adjusting for matlab's indexing, then +0.5 for
    # location in grid
    path = path_data + 0.5;
    # Find indices where we cross a grid border
    indices = [];
    for idx = 2:len(path)
        if ((path(idx,1) + path(idx-1,1) == len(final_grid)) && path(idx,1) ~= path(idx-1,1))  ...
                       || ((path(idx,2) + path(idx-1,2) == len(final_grid(1,:))) && path(idx,2) ~= path(idx-1,2))
            indices = [indices,idx];
#        end
#    end
    indices = [indices,len(path)+1];
    figure;
    show(map);
    set(gca, 'YDir', 'reverse');
    grid minor;
    hold on;
    plot(path(1:(indices(1)-1),1),path(1:(indices(1)-1),2), 'r', 'LineWidth', 2);
    for i = 2:len(indices)
        plot(path(indices(i-1):(indices(i)-1),1),path(indices(i-1):(indices(i)-1),2), 'r', 'LineWidth', 2);
#    end

    print('\tRAN\n');
#end
## Epochs of food gathering
if option_food_gather
    print('RUNNING Food Gathering Analysis...');
    if ~isempty(collected_food)
        cf_index = 1;
        times = zeros(1,len(collected_food(:,1)));
        for i = 1:len(path(:,1))
            if (path(i,:)-0.5) == collected_food(cf_index,:)
                times(cf_index) = i;
                cf_index = cf_index + 1;
                if cf_index >= len(collected_food(:,1))
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
    #plot(1:len(times),times);
    histogram(times,20);
    title('Times of gathered food')
    xlabel('Epoch');
    ylabel('Number of food gathered');

    subplot(1,2,2);
    performance_100 = zeros(1,num_epochs);
    for e = 1:num_epochs
        performance_100(e) = len(times(times <= e & times > max(0,e-100)))/100;
    end
    fit_gather = polyfit(1:num_epochs,performance_100,1);
    yfit_gather = polyval(fit_gather,1:num_epochs);
    plot(1:num_epochs, performance_100);
    hold on;
    plot(1:num_epochs, yfit_gather, 'LineWidth', 2);
    title('Performance over last 100 Epochs');
    xlabel('Epoch');
    ylabel('Gathering Rate');

    print('\tRAN\n');
end
## Output cell Frequencies
if option_output_freqs
    print('RUNNING Output Cell Frequency Analysis...');
    if ~isempty(output_cell_frequencies)
        figure;
        hold on;
        for cell = 1:len(output_cell_frequencies(1,:))
            plot(1:len(output_cell_frequencies(:,cell)), output_cell_frequencies(:,cell));
        end
    end
    xlabel('Epochs');
    ylabel('Frequency (Hz)');
    title('Output Cell Frequencies');

    print('\tRAN\n');
end
## Spiking data
if option_spiking_data
    print('RUNNING Spiking Data Analysis...');
    epoch_spike_indices = floor(spkt/300);
    spikes_per_epoch = zeros(1,num_epochs);
    for e = 1:num_epochs
        spikes_per_epoch(e) = len(spkid(epoch_spike_indices == e & spkid > (max(spkid)-9)));
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

    print('\tRAN\n');
end
## Animation
if option_animate
    print('RUNNING Path Animation...');
    # Animation
    figure;
    show(map);
    grid on;
    set(gca, 'YDir', 'reverse');
    hold on;
    index = 1;
    for i = 2:len(path)
        if i ~= indices(index)
            plot(path(i-1:i, 1),path(i-1:i, 2), 'r', 'LineWidth', 2);
        else
            index = index + 1;
        end
        pause(1/animate_speed);
    end
    print('\tRAN\n');
end