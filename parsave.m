function parsave(fname, ResultsGroup)

    % Make sure Repositories folder exists
    if ~exist('Repositories', 'dir')
        mkdir('Repositories');
    end

    % Now safe to save
    save(fname, 'ResultsGroup');

end