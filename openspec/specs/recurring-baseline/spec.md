# Recurring Baseline Specification

## Purpose

Produces the monthly recurring spending figure — a measurement of complete months, robust to one strange month — and keeps large one-time items out of it so a short window does not lie.

## Requirements

### Requirement: Only complete months count
The baseline SHALL be computed over calendar months that lie entirely within the observed window. Partial months at either end SHALL be excluded and the number of complete months printed.

#### Scenario: Window starts mid-month
- **WHEN** the earliest transaction is 2026-01-15 and the latest is 2026-04-30
- **THEN** February, March and April are the complete months and January is excluded

### Requirement: The baseline is a median
The monthly recurring figure SHALL be the median of complete-month totals, annualised by twelve.

#### Scenario: One outlying month
- **WHEN** complete months total 4,000, 4,100, 4,050 and 9,000
- **THEN** RECURRING is 4,075 per month, not the mean

### Requirement: Irregular means large and non-repeating
A transaction at or above `--lumpy` SHALL be held out of the baseline only if its description signature does not recur in at least three distinct months. Large recurring payments SHALL stay in the baseline.

#### Scenario: Mortgage
- **WHEN** `Mortgage payment #4985` of 3,444 appears in every month
- **THEN** it is part of RECURRING and is not listed under IRREGULAR

#### Scenario: One-time repair
- **WHEN** a 7,654 charge appears once
- **THEN** it is excluded from the baseline and listed under IRREGULAR with its date and description

### Requirement: Description signatures ignore reference numbers
Two descriptions SHALL be treated as the same recurring payment when they share the same first two alphabetic words after runs of three or more digits or `#` are removed.

#### Scenario: Reference number changes monthly
- **WHEN** one month reads `Mortgage payment #498539-3` and another `Mortgage payment Term Life, Travel`
- **THEN** both count toward the same signature

### Requirement: Month-end obligations can be levelled
An obligation listed under `level` in `rules.yml` SHALL be charged to each complete month at its rate — total paid within complete months divided by the number of complete months — rather than on the dates its transfers cleared. Levelling SHALL apply only when at least three matching transfers exist, and the levelled amount and count SHALL be printed.

#### Scenario: Payment split by a transfer cap across a month boundary
- **WHEN** a levelled obligation clears as 3,000 on the 31st and 685 on the 2nd of the next month
- **THEN** neither month is charged those amounts on those dates; each complete month is charged the obligation's monthly rate

#### Scenario: Too few payments to level
- **WHEN** a `level` pattern matches only two transfers in the window
- **THEN** they are left on the dates they cleared and no LEVELLED line is printed

### Requirement: Decided items stop being questions
An irregular item pinned under `one_off` SHALL be listed under ONE-OFF with its note rather than under IRREGULAR, and SHALL remain outside the baseline.

#### Scenario: Repair judged one-time
- **WHEN** the 7,654 charge is pinned with a note
- **THEN** it appears under ONE-OFF with that note and IRREGULAR no longer lists it

### Requirement: Stability is stated, not assumed
The tool SHALL print the range of complete-month totals as a percentage of the median and label the baseline `steady` only when the highest month is at most 135% and the lowest at least 75% of the median; otherwise it SHALL label the annual figure as soft.

#### Scenario: Even months
- **WHEN** months range from 90% to 109% of median
- **THEN** the line ends `steady`

#### Scenario: Uneven months
- **WHEN** any month is below 75% or above 135% of median
- **THEN** the line ends with a warning that the annual figure is soft
