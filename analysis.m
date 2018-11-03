clear all
close all

data = jsondecode(fileread('database-export.json'));

good = [];          %first column is value, second is timestamp
bad = [];

for i = 1:length(data)
    history = data(i).history;
    for j = 1:length(history)
        type = history(j).type;
        if type == "good"
            good(1, end + 1) = history(j).value;
            good(2, end) = history(j).timestamp;
        else
            bad(1, end + 1) = history(j).value;
            bad(2, end) = history(j).timestamp;
        end
    end
end

[~, i] = sort(good(2, :));

goodSorted = zeros(size(good));
goodSorted(1, :) = good(1, i);
goodSorted(2, :) = good(2, i);

[~, j] = sort(bad(2, :));

badSorted = zeros(size(bad));
badSorted(1, :) = bad(1, j);
badSorted(2, :) = bad(2, j);

all(1, :) = [goodSorted(1, :), -badSorted(1, :)];
all(2, :) = [goodSorted(2, :), badSorted(2, :)];

[~, k] = sort(all(2, :));
all(1, :) = all(1, k);
all(2, :) = all(2, k);

startDate = datetime(datetime(goodSorted(2, 1), 'ConvertFrom', 'posixtime').Year, datetime(goodSorted(2, 1), 'ConvertFrom', 'posixtime').Month, datetime(goodSorted(2, 1), 'ConvertFrom', 'posixtime').Day);
endDate = datetime(datetime(badSorted(2, end), 'ConvertFrom', 'posixtime').Year, datetime(badSorted(2, end), 'ConvertFrom', 'posixtime').Month, datetime(badSorted(2, end), 'ConvertFrom', 'posixtime').Day);

days = startDate:endDate;
points = zeros(3, length(days));

%for d = 1:length(days)
%    for i  = 1:length(goodSorted)
%        goodDt = datetime(goodSorted(2, i), 'ConvertFrom', 'posixtime');
%        if datetime(goodDt.Year, goodDt.Month, goodDt.Day) == days(d)
%            points(1, d) = points(1, d) + goodSorted(1, i);
%        end
%    end
%    for i  = 1:length(badSorted)
%        badDt = datetime(badSorted(2, i), 'ConvertFrom', 'posixtime');
%        if datetime(badDt.Year, badDt.Month, badDt.Day)== days(d)
%            points(2, d) = points(2, d) + badSorted(1, i);
%        end
%    end
%    for i  = 1:length(all)
%        allDt = datetime(all(2, i), 'ConvertFrom', 'posixtime');
%        if datetime(allDt.Year, allDt.Month, allDt.Day)== days(d)
%            points(3, d) = points(3, d) + all(1, i);
%        end
%    end
%end


goodDate = datetime(goodSorted(2, :), 'ConvertFrom', 'posixtime' );
badDate = datetime(badSorted(2, :), 'ConvertFrom', 'posixtime' );
allDate = datetime(all(2, :), 'ConvertFrom', 'posixtime' );

datesGoodShifted = dateshift(goodDate, 'start', 'day');
datesBadShifted = dateshift(badDate, 'start', 'day');

goodSums = splitapply(@sum, goodSorted(1,:), findgroups(datesGoodShifted));
badSums = splitapply(@sum, badSorted(1,:), findgroups(datesBadShifted));

%error('asd');

goodDate.Format = 'dd-MMMM-yyyy';
badDate.Format = 'dd-MMMM-yyyy';
allDate.Format = 'dd-MMMM-yyyy';

figure 
hold on
%grid on
datetick('x','dd-mm-yyyy','keeplimits','keepticks')
plot(days, cumsum(goodSums))
plot(days, cumsum(badSums))
plot(days, cumsum(goodSums - badSums))
legend('Hyvinvointi', 'Pahoinvointi', 'Pisteiden erotus')
ylabel('Pisteet')
