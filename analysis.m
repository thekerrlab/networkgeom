% PHYS2921
% William Talbot
% SSP Neural Net Analysis

clc;
clear;
close all;

% Options
animate = false;
animate_speed = 100; % Frequency

% Read files
perf = csvread('csvfiles/performances.csv');
sumW = csvread('csvfiles/weights_sum.csv');
meanW = csvread('csvfiles/weights_mean.csv');
varW = csvread('csvfiles/weights_var.csv');
%init_weights = csvread('csvfiles/weights_init.csv');
%final_weights = csvread('csvfiles/weights_final.csv');
exc_stdp_weights = csvread('csvfiles/exc_stdp_weights.csv');
inh_weights = csvread('csvfiles/inh_weights.csv');
init_exc_stdp_weights = exc_stdp_weights(1,:);
final_exc_stdp_weights = exc_stdp_weights(end,:);
init_inh_weights = inh_weights(1,:);
final_inh_weights = inh_weights(end,:);
path_data = csvread('csvfiles/path.csv');
try
    collected_food = csvread('csvfiles/collected_food.csv');
catch
    collected_food = [];
end
final_grid = csvread('csvfiles/final_grid.csv');
try
    output_cell_frequencies = csvread('csvfiles/output_cell_frequencies.csv');
catch
    output_cell_frequencies = [];
end

fprintf('Initial Sum Weight of Excitatory STDP Connections = %.3e\n', sum(init_exc_stdp_weights));
fprintf('Final Sum Weight of Excitatory STDP Connections = %.3e\n', sum(final_exc_stdp_weights));
fprintf('Initial Sum Weight of Inhibitory Connections = %.3e\n', sum(init_inh_weights));
fprintf('Final Sum Weight of Inhibitory Connections = %.3e\n', sum(final_inh_weights));


%% Performance and Diagnostics
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

%% Weights histogram
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

%% Weights distribution
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

%% Plot the occupancy grid and the path
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

%% Epochs of food gathering
cf_index = 1;
times = zeros(1,length(collected_food(:,1)));
for i = 1:length(path(:,1))
    if (path(i,:)-0.5) == collected_food(cf_index,:)
        times(cf_index) = i;
        cf_index = cf_index + 1;
        if cf_index == length(collected_food(:,1))
            break;
        end
    end
end
times = times(times > 0);
figure;
%plot(1:length(times),times);
histogram(times,20);
title('Times of gathered food')
xlabel('Epoch');
ylabel('Number of food gathered');

%% Output cell Frequencies
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

%% Animation
if animate
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
end