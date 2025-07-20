from import_mapper.core.mapper import ImportMapper

def test_run_analysis_empty():
    mapper = ImportMapper(".", detailed=False)
    result = mapper.run_analysis()
    assert "dependency_map" in result
