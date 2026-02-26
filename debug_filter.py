#!/usr/bin/env python
import requests
import json

# First, get the available website filter options
print('Step 1: Getting available filter options...\n')
r = requests.get('http://localhost:5000/api/filters',
                 headers={'Authorization': 'Bearer t_hmXetfMCq3'})

if r.status_code == 200:
    data = r.json()
    websites = data.get('filters', {}).get('websites', [])
    print(f'Available websites ({len(websites)} total):')
    for w in websites[:5]:  # Show first 5
        print(f'  - {w}')
    if len(websites) > 5:
        print(f'  ... and {len(websites) - 5} more')

    # Now filter by "Filter-technik.de" if it exists
    target = 'Filter-technik.de'
    if target in websites:
        print(f'\nStep 2: Testing filter with website="{target}"...')
        print(
            f'Making request to: /api/projects/search?website={target}&limit=1000\n')

        r2 = requests.get(f'http://localhost:5000/api/projects/search?website={target}&limit=1000',
                          headers={'Authorization': 'Bearer t_hmXetfMCq3'})

        if r2.status_code == 200:
            data2 = r2.json()
            projects = data2.get('projects', [])
            by_website = data2.get('by_website', [])

            print(f'Results:')
            print(f'  Total projects in result: {len(projects)}')
            print(f'  Website groups: {len(by_website)}')
            print(f'\nWebsite groups found:')
            for group in by_website:
                website = group.get('website', 'Unknown')
                count = group.get('project_count', 0)
                print(f'  - {website}: {count} projects')

                # Show sample project titles
                for proj in group.get('projects', [])[:2]:
                    title = proj.get('title', 'Unknown')[:60]
                    print(f'      * {title}')
        else:
            print(f'Error: {r2.status_code}')
            print(r2.text)
    else:
        print(f'\n"{target}" not found in website list')
        print('First 3 websites:', websites[:3])
else:
    print(f'Error getting filters: {r.status_code}')
